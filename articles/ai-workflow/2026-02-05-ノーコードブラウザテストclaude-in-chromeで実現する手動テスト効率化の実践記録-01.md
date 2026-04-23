---
id: "2026-02-05-ノーコードブラウザテストclaude-in-chromeで実現する手動テスト効率化の実践記録-01"
title: "【ノーコード】ブラウザテスト：Claude in Chromeで実現する手動テスト効率化の実践記録"
url: "https://qiita.com/mo-shimizu-tb/items/9232efe0417534d07cee"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-02-05"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

```
import React, { useState } from 'react';
import { Play, RotateCcw, Download, Settings, CheckCircle, XCircle, Clock, AlertCircle, ChevronDown, ChevronRight, FileText, Upload } from 'lucide-react';

const testCasesData = [];

export default function TestTool() {
  const [testCases, setTestCases] = useState([]);
  const [markdownInput, setMarkdownInput] = useState('');
  const [showMarkdownInput, setShowMarkdownInput] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState('全て');
  const [expandedTests, setExpandedTests] = useState({});
  const [testAccount, setTestAccount] = useState({
    email: '',
    password: ''
  });
  const [isRunning, setIsRunning] = useState(false);
  const [currentTestIndex, setCurrentTestIndex] = useState(-1);
  const [testResults, setTestResults] = useState([]);
  const [logs, setLogs] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    screenshotOnError: true,
    screenshotOnSuccess: false,
    waitTime: 1000
  });

  const groups = ['全て', ...Array.from(new Set(testCases.map(tc => tc.group)))];
  const filteredCases = selectedGroup === '全て' ? testCases : testCases.filter(tc => tc.group === selectedGroup);

  const parseMarkdown = (markdown) => {
    const cases = [];
    const sections = markdown.split(/(?=### TC-[A-Z]+-\d+:)/);
    
    sections.forEach(section => {
      if (!section.trim() || !section.includes('### TC-')) return;
      
      const lines = section.split('\n').filter(line => line.trim());
      
      // テストケースID と名前
      const titleMatch = lines[0].match(/### (TC-[A-Z]+-\d+): (.+)/);
      if (!titleMatch) return;
      
      const id = titleMatch[1];
      const name = titleMatch[2];
      
      // グループ名を推測
      let group = 'その他';
      if (id.startsWith('TC-MOD-')) group = 'モーダル操作';
      else if (id.startsWith('TC-TAB-')) group = 'タブ切り替え';
      else if (id.startsWith('TC-FIL-')) group = 'フィルタリング';
      else if (id.startsWith('TC-TMP-')) group = 'テンプレート選択';
      else if (id.startsWith('TC-AI-')) group = 'AI生成';
      else if (id.startsWith('TC-EDT-')) group = 'エディタ基本操作';
      else if (id.startsWith('TC-SAV-')) group = '保存・公開';
      else if (id.startsWith('TC-ERR-')) group = 'エラーシナリオ';
      else if (id.startsWith('TC-E2E-')) group = 'E2Eシナリオ';
      
      // 優先度
      let priority = '中';
      const priorityLine = lines.find(l => l.includes('**優先度**:'));
      if (priorityLine) {
        if (priorityLine.includes('高')) priority = '高';
        else if (priorityLine.includes('低')) priority = '低';
      }
      
      // 前提条件
      const preconditions = [];
      let inPreconditions = false;
      let inSteps = false;
      let inExpected = false;
      
      const steps = [];
      let expectedResult = '';
      let stepCount = 0;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        if (line.includes('**前提条件**:')) {
          inPreconditions = true;
          inSteps = false;
          inExpected = false;
          continue;
        }
        
        if (line.includes('**テスト手順**:')) {
          inPreconditions = false;
          inSteps = true;
          inExpected = false;
          continue;
        }
        
        if (line.includes('**期待結果**:')) {
          inPreconditions = false;
          inSteps = false;
          inExpected = true;
          continue;
        }
        
        if (inPreconditions && line.startsWith('- ')) {
          preconditions.push(line.substring(2).trim());
        }
        
        if (inSteps && line.match(/^\d+\./)) {
          stepCount++;
          const stepText = line.replace(/^\d+\.\s*/, '').trim();
          
          // URLの抽出
          let url = null;
          const urlMatch = stepText.match(/`(https?:\/\/[^`]+)`/);
          if (urlMatch) url = urlMatch[1];
          
          // アクション部分と期待結果の分離
          let action = stepText;
          let expected = '';
          
          // 次の行に期待結果があるかチェック
          if (i + 1 < lines.length && !lines[i + 1].match(/^\d+\./)) {
            expected = lines[i + 1].trim();
          }
          
          steps.push({
            step: stepCount,
            action: action.replace(/`[^`]+`/, '').trim(),
            url: url,
            expected: expected || 'ステップが完了する'
          });
        }
        
        if (inExpected && line.startsWith('- ')) {
          expectedResult += (expectedResult ? '\n' : '') + line.substring(2).trim();
        } else if (inExpected && line.trim() && !line.startsWith('**') && !line.startsWith('###')) {
          expectedResult += (expectedResult ? ' ' : '') + line.trim();
        }
      }
      
      cases.push({
        id,
        name,
        group,
        priority,
        status: 'pending',
        preconditions: preconditions.length > 0 ? preconditions : ['前提条件なし'],
        steps: steps.length > 0 ? steps : [{ step: 1, action: 'テスト手順を実行', expected: '正常に完了する' }],
        expectedResult: expectedResult || '期待する結果が得られる'
      });
    });
    
    return cases;
  };

  const handleLoadMarkdown = () => {
    if (!markdownInput.trim()) {
      addLog('マークダウンテキストを入力してください', 'error');
      return;
    }
    
    try {
      const parsedCases = parseMarkdown(markdownInput);
      setTestCases(parsedCases);
      addLog(`${parsedCases.length}件のテストケースを読み込みました`, 'success');
      setShowMarkdownInput(false);
    } catch (error) {
      addLog(`マークダウンの解析に失敗しました: ${error.message}`, 'error');
    }
  };

  const toggleTestExpand = (testId) => {
    setExpandedTests(prev => ({ ...prev, [testId]: !prev[testId] }));
  };

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString('ja-JP');
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const handleStartTest = () => {
    setIsRunning(true);
    setTestResults([]);
    setLogs([]);
    
    addLog('=== テスト実行計画 ===', 'info');
    addLog('', 'info');
    addLog(`📋 実行対象: ${filteredCases.length}件のテストケース`, 'info');
    addLog(`👤 テストアカウント: ${testAccount.email}`, 'info');
    addLog(`🔑 パスワード: ${testAccount.password}`, 'info');
    addLog('', 'info');
    addLog('【実行するテストケース】', 'info');
    
    filteredCases.forEach((testCase, index) => {
      addLog(`${index + 1}. ${testCase.id}: ${testCase.name} (優先度: ${testCase.priority})`, 'info');
    });
    
    addLog('', 'info');
    addLog('【実行手順】', 'info');
    addLog('1. Claude in Chromeでブラウザタブを作成', 'info');
    addLog('2. ログイン画面にアクセスしてログイン', 'info');
    addLog('3. 各テストケースを順番に実行', 'info');
    addLog('4. 各ステップの結果を記録', 'info');
    addLog('5. エラー時はスクリーンショットを撮影', 'info');
    addLog('6. テスト結果をwindow.storageに保存', 'info');
    addLog('7. 完了後、「結果を同期」ボタンで結果を取得', 'info');
    addLog('', 'info');
    addLog('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'warning');
    addLog('', 'warning');
    addLog('✅ この内容で実行しますか？', 'warning');
    addLog('', 'warning');
    addLog('👉 チャット欄に以下のいずれかを入力してください:', 'warning');
    addLog('   • 「はい」または「実行してください」→ テストを開始', 'warning');
    addLog('   • 「いいえ」または「キャンセル」→ 実行を中止', 'warning');
    addLog('', 'warning');
    addLog('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'warning');
  };

  const handleSyncResults = () => {
    addLog('', 'info');
    addLog('=== テスト結果の同期を開始します ===', 'info');
    addLog('', 'info');
    addLog('Claudeからテスト結果を取得しています...', 'info');
    addLog('', 'info');
    addLog('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'warning');
    addLog('', 'warning');
    addLog('👉 Claudeがテスト結果を報告するのを待っています...', 'warning');
    addLog('', 'warning');
    addLog('結果が報告されたら自動的に反映されます', 'warning');
    addLog('', 'warning');
    addLog('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'warning');
  };

  const handleResetTest = () => {
    setIsRunning(false);
    setCurrentTestIndex(-1);
    setTestResults([]);
    setLogs([]);
  };

  const exportReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      testAccount: testAccount.email,
      totalTests: testResults.length,
      passed: testResults.filter(r => r.status === 'passed').length,
      failed: testResults.filter(r => r.status === 'failed').length,
      results: testResults,
      logs: logs
    };
    
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `test-report-${Date.now()}.json`;
    link.click();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed': return <CheckCircle className="text-green-600" size={20} />;
      case 'failed': return <XCircle className="text-red-600" size={20} />;
      case 'running': return <Clock className="text-blue-600 animate-spin" size={20} />;
      default: return <Clock className="text-gray-400" size={20} />;
    }
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="text-green-600" size={16} />;
      case 'error': return <XCircle className="text-red-600" size={16} />;
      case 'warning': return <AlertCircle className="text-yellow-600" size={16} />;
      default: return <AlertCircle className="text-blue-600" size={16} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case '高': return 'text-red-600 bg-red-50';
      case '中': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-green-600 bg-green-50';
    }
  };

  const passedCount = testResults.filter(r => r.status === 'passed').length;
  const failedCount = testResults.filter(r => r.status === 'failed').length;
  const totalTests = filteredCases.length;
  const progress = testResults.length > 0 ? (testResults.length / totalTests) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">テスト実行ツール</h1>
              <p className="text-gray-600 mt-1">テストケース管理と自動実行</p>
            </div>
            <button onClick={() => setShowSettings(!showSettings)} className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
              <Settings size={24} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">テストアカウント</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
                  <input type="email" value={testAccount.email} onChange={(e) => setTestAccount({...testAccount, email: e.target.value})} disabled={isRunning} className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">パスワード</label>
                  <input type="password" value={testAccount.password} onChange={(e) => setTestAccount({...testAccount, password: e.target.value})} disabled={isRunning} className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100" />
                </div>
              </div>
            </div>

            {showSettings && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">テスト設定</h2>
                <div className="space-y-3">
                  <label className="flex items-center gap-2">
                    <input type="checkbox" checked={settings.screenshotOnError} onChange={(e) => setSettings({...settings, screenshotOnError: e.target.checked})} className="w-4 h-4" />
                    <span className="text-sm text-gray-700">エラー時にスクリーンショット</span>
                  </label>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">テスト実行</h2>
              <div className="space-y-3">
                <button onClick={() => setShowMarkdownInput(!showMarkdownInput)} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold">
                  <FileText size={20} />
                  {showMarkdownInput ? 'マークダウン入力を閉じる' : 'マークダウンから読込'}
                </button>
                <button onClick={handleStartTest} disabled={isRunning || testCases.length === 0} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold disabled:opacity-50">
                  <Play size={20} />
                  {isRunning ? 'テスト実行中...' : 'テスト開始'}
                </button>
                <button onClick={handleSyncResults} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-semibold">
                  <Download size={20} />
                  結果を同期
                </button>
                <button onClick={handleResetTest} disabled={isRunning} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold disabled:opacity-50">
                  <RotateCcw size={20} />
                  リセット
                </button>
                {testResults.length > 0 && (
                  <button onClick={exportReport} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold">
                    <Download size={20} />
                    レポート出力
                  </button>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">実行統計</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">総テスト数</span>
                  <span className="font-semibold text-gray-900">{totalTests}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-green-600">成功</span>
                  <span className="font-semibold text-green-600">{passedCount}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-red-600">失敗</span>
                  <span className="font-semibold text-red-600">{failedCount}</span>
                </div>
                <div className="pt-3 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600">進捗</span>
                    <span className="font-semibold text-gray-900">{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className="bg-blue-600 h-3 rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {showMarkdownInput && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">マークダウンテキスト入力</h2>
                <p className="text-sm text-gray-600 mb-3">テストケースのマークダウンテキストを貼り付けてください</p>
                <textarea value={markdownInput} onChange={(e) => setMarkdownInput(e.target.value)} className="w-full h-64 px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm" placeholder="### TC-MOD-001: テストケース名
**優先度**: 高

**前提条件**:
- 条件1
- 条件2

**テスト手順**:
1. 手順1
2. 手順2

**期待結果**:
- 期待される結果" />
                <div className="flex gap-3 mt-4">
                  <button onClick={handleLoadMarkdown} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold">
                    読み込む
                  </button>
                  <button onClick={() => setMarkdownInput('')} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold">
                    クリア
                  </button>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex gap-2 overflow-x-auto">
                {groups.map(group => (
                  <button key={group} onClick={() => setSelectedGroup(group)} className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${selectedGroup === group ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                    {group}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">テストケース一覧</h2>
                {testCases.length === 0 && (
                  <span className="text-sm text-gray-500">マークダウンを読み込んでください</span>
                )}
              </div>
              {testCases.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <FileText size={48} className="mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium mb-2">テストケースが読み込まれていません</p>
                  <p className="text-sm">「マークダウンから読込」ボタンをクリックしてテストケースを追加してください</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {filteredCases.map((testCase, index) => {
                  const result = testResults.find(r => r.id === testCase.id);
                  const isCurrent = currentTestIndex === index && isRunning;
                  const isExpanded = expandedTests[testCase.id];
                  
                  return (
                    <div key={testCase.id} className={`rounded-lg border transition ${isCurrent ? 'bg-blue-50 border-blue-300' : result?.status === 'passed' ? 'bg-green-50 border-green-300' : result?.status === 'failed' ? 'bg-red-50 border-red-300' : 'bg-gray-50 border-gray-200'}`}>
                      <div className="flex items-center gap-3 p-4 cursor-pointer hover:bg-opacity-80" onClick={() => toggleTestExpand(testCase.id)}>
                        <div className="flex-shrink-0">
                          {getStatusIcon(isCurrent ? 'running' : result?.status || 'pending')}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-mono text-sm font-semibold text-gray-700">{testCase.id}</span>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(testCase.priority)}`}>{testCase.priority}</span>
                          </div>
                          <p className="text-sm font-semibold text-gray-900">{testCase.name}</p>
                          <p className="text-xs text-gray-600 mt-0.5">{testCase.group}</p>
                        </div>
                        <div className="flex-shrink-0">
                          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="px-4 pb-4 border-t border-gray-200 pt-4 space-y-4">
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">前提条件</h4>
                            <ul className="list-disc list-inside space-y-1">
                              {testCase.preconditions.map((condition, idx) => (
                                <li key={idx} className="text-sm text-gray-700">{condition}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">テスト手順</h4>
                            <div className="space-y-2">
                              {testCase.steps.map((step) => (
                                <div key={step.step} className="bg-white p-3 rounded border border-gray-200">
                                  <div className="flex gap-3">
                                    <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-semibold">{step.step}</div>
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm font-medium text-gray-900 mb-1">{step.action}</p>
                                      {step.url && <p className="text-xs text-gray-600 mb-1"><span className="font-medium">URL:</span> {step.url}</p>}
                                      <p className="text-xs text-green-700 mt-1"><span className="font-medium">期待:</span> {step.expected}</p>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">期待結果</h4>
                            <p className="text-sm text-gray-700 bg-white p-3 rounded border border-gray-200">{testCase.expectedResult}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              )}
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">実行ログ</h2>
              <div className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto font-mono text-sm">
                {logs.length === 0 ? (
                  <p className="text-gray-400">ログはまだありません</p>
                ) : (
                  <div className="space-y-1">
                    {logs.map((log, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <span className="text-gray-500 flex-shrink-0">[{log.timestamp}]</span>
                        <div className="flex items-start gap-2 flex-1">
                          {getLogIcon(log.type)}
                          <span className={log.type === 'success' ? 'text-green-400' : log.type === 'error' ? 'text-red-400' : log.type === 'warning' ? 'text-yellow-400' : 'text-gray-300'}>{log.message}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```
