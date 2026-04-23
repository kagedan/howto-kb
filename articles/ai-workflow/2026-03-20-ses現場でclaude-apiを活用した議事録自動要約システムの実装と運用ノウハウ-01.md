---
id: "2026-03-20-ses現場でclaude-apiを活用した議事録自動要約システムの実装と運用ノウハウ-01"
title: "SES現場でClaude APIを活用した議事録自動要約システムの実装と運用ノウハウ"
url: "https://qiita.com/sescore/items/80a9af046eef5aae59d0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

```
import Fastify, { FastifyInstance } from 'fastify';
import multipart from '@fastify/multipart';
import cors from '@fastify/cors';
import { AudioTranscriber, TranscriptionResult } from './transcriber';
import { MeetingSummarizer, MeetingSummary } from './summarizer';
import { SlackNotifier } from './slack-notifier';
import path from 'path';
import fs from 'fs/promises';

interface ProcessingJob {
  id: string;
  status: 'processing' | 'completed' | 'error';
  result?: MeetingSummary;
  error?: string;
  createdAt: Date;
}

class MeetingMinutesServer {
  private server: FastifyInstance;
  private transcriber: AudioTranscriber;
  private summarizer: MeetingSummarizer;
  private slackNotifier: SlackNotifier;
  private jobs: Map<string, ProcessingJob> = new Map();

  constructor(
    openaiApiKey: string,
    claudeApiKey: string,
    slackWebhookUrl?: string
  ) {
    this.server = Fastify({ 
      logger: { level: 'info' },
      bodyLimit: 104857600 // 100MB
    });
    
    this.transcriber = new AudioTranscriber(openaiApiKey);
    this.summarizer = new MeetingSummarizer(claudeApiKey);
    this.slackNotifier = new SlackNotifier(slackWebhookUrl);
    
    this.setupMiddleware();
    this.setupRoutes();
  }

  private async setupMiddleware(): Promise<void> {
    await this.server.register(multipart, {
      limits: {
        fileSize: 100 * 1024 * 1024 // 100MB
      }
    });
    
    await this.server.register(cors, {
      origin: true
    });
  }

  private setupRoutes(): void {
    // 音声ファイルアップロードエンドポイント
    this.server.post('/api/upload-meeting', {
      schema: {
        consumes: ['multipart/form-data'],
        response: {
          200: {
            type: 'object',
            properties: {
              jobId: { type: 'string' },
              message: { type: 'string' }
            }
          }
        }
      }
    }, async (request, reply) => {
      try {
        const data = await request.file();
        if (!data) {
          return reply.code(400).send({ error: 'ファイルが指定されていません' });
        }

        // ファイル検証
        const allowedMimeTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'video/mp4'];
        if (!allowedMimeTypes.includes(data.mimetype)) {
          return reply.code(400).send({ 
            error: 'サポートされていないファイル形式です。MP3, WAV, MP4のみ対応しています。' 
          });
        }

        // 一時ファイルに保存
        const jobId = this.generateJobId();
        const tempDir = path.join(process.cwd(), 'temp');
        await fs.mkdir(tempDir, { recursive: true });
        
        const tempFilePath = path.join(tempDir, `${jobId}.${this.getFileExtension(data.mimetype)}`);
        await data.file.pipe(require('fs').createWriteStream(tempFilePath));

        // 非同期処理開始
        const job: ProcessingJob = {
          id: jobId,
          status: 'processing',
          createdAt: new Date()
        };
        
        this.jobs.set(jobId, job);
        
        // バックグラウンド処理
        this.processAudioFile(jobId, tempFilePath, {
          title: request.body?.title as string,
          expectedParticipants: request.body?.participants as string[],
          slackChannel: request.body?.slackChannel as string
        }).catch(error => {
          console.error(`Job ${jobId} processing error:`, error);
          this.jobs.set(jobId, {
            ...job,
            status: 'error',
            error: error.message
          });
        });

        return reply.send({
          jobId,
          message: '処理を開始しました。進捗は /api/job/{jobId} で確認できます。'
        });
        
      } catch (error) {
        console.error('Upload error:', error);
        return reply.code(500).send({ error: 'ファイルアップロードに失敗しました' });
      }
    });

    // ジョブ状態確認エンドポイント
    this.server.get('/api/job/:jobId', async (request, reply) => {
      const { jobId } = request.params as { jobId: string };
      const job = this.jobs.get(jobId);
      
      if (!job) {
        return reply.code(404).send({ error: 'ジョブが見つかりません' });
      }
      
      return reply.send(job);
    });

    // 健全性チェック
    this.server.get('/health', async () => {
      return { status: 'OK', timestamp: new Date().toISOString() };
    });
  }

  /**
   * 音声ファイルの非同期処理メイン関数
   */
  private async processAudioFile(
    jobId: string,
    filePath: string,
    options: {
      title?: string;
      expectedParticipants?: string[];
      slackChannel?: string;
    }
  ): Promise<void> {
    try {
      console.log(`Job ${jobId}: 音声認識開始`);
      const transcription = await this.transcriber.transcribeAudio(filePath);
      
      console.log(`Job ${jobId}: 議事録要約開始`);
      const summary = await this.summarizer.summarizeMeeting(
        transcription.text,
        {
          title: options.title,
          expectedParticipants: options.expectedParticipants
        }
      );
      
      // ジョブ完了
      this.jobs.set(jobId, {
        id: jobId,
        status: 'completed',
        result: summary,
        createdAt: this.jobs.get(jobId)!.createdAt
      });
      
      // Slack通知（オプション）
      if (options.slackChannel) {
        await this.slackNotifier.sendMeetingMinutes(summary, options.slackChannel);
      }
      
      console.log(`Job ${jobId}: 処理完了`);
      
    } catch (error) {
      console.error(`Job ${jobId}: 処理エラー`, error);
      throw error;
    } finally {
      // 一時ファイル削除
      try {
        await fs.unlink(filePath);
      } catch (cleanupError) {
        console.error('Temp file cleanup error:', cleanupError);
      }
    }
  }

  private generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }

  private getFileExtension(mimeType: string): string {
    const mimeMap: { [key: string]: string } = {
      'audio/mpeg': 'mp3',
      'audio/wav': 'wav',
      'audio/mp4': 'm4a',
      'video/mp4': 'mp4'
    };
    return mimeMap[mimeType] || 'unknown';
  }

  async start(port: number = 3000): Promise<void> {
    try {
      await this.server.listen({ port, host: '0.0.0.0' });
      console.log(`Meeting Minutes Server started on port ${port}`);
    } catch (error) {
      console.error('Server start error:', error);
      process.exit(1);
    }
  }
}

// サーバー起動
if (require.main === module) {
  const server = new MeetingMinutesServer(
    process.env.OPENAI_API_KEY!,
    process.env.CLAUDE_API_KEY!,
    process.env.SLACK_WEBHOOK_URL
  );
  
  server.start(parseInt(process.env.PORT || '3000'));
}

export { MeetingMinutesServer };
```
