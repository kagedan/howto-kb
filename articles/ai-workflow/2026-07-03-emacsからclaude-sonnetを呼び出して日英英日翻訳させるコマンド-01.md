---
id: "2026-07-03-emacsからclaude-sonnetを呼び出して日英英日翻訳させるコマンド-01"
title: "EmacsからClaude Sonnetを呼び出して日英(英日)翻訳させるコマンド"
url: "https://qiita.com/masatoi0/items/85cab8902e6d1430bedd"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "GPT", "qiita"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

以前DeepLのAPIを呼び出して、Emacsで選択したリージョン内の文字列を判別して和英、英和した結果をクリップボードにコピーするというコマンドを作ったという記事を書いた。

https://qiita.com/masatoi0/items/26c7384749393a1bf8fb

しかし、最近は翻訳の品質に不満を感じてきていて、gptelでClaude sonnetに翻訳させた方が結果が良いと思うようになった。
gptelでもリージョン選択してその直後の位置に問合せ結果を書き出すことができるので一応翻訳はできるのだが、deepl.elと同様の使用感にしたかったので、自分でコマンドを書くことにした。

外部APIを呼び出すので秘匿情報を含んだ文章を送らないようにする注意は必要。
また、requestパッケージに依存するのでインストールしておく。

claude-translate.el
```elisp
;;; claude-translate.el --- Translate region with Claude -*- lexical-binding: t; -*-

;;; Install
;; requestが必要なので M-x package-install request などでインストールしておく
;; init.elなどでロードする
;; (load-file "/path/to/claude-translate.el")
;; AnthropicのAPIキーを設定しておく
;; (setq claude-api-key "sk-ant-...")
;; または環境変数 ANTHROPIC_API_KEY を設定しておく
;; キーバインドを設定しておく
;; (global-set-key (kbd "C-c t") 'claude-translate)

;;; Usage
;; 翻訳したい部分をリージョン選択して設定したキーバインド、または M-x claude-translate
;; 翻訳結果がミニバッファに出る。また、同じ内容がクリップボードにコピーされている

(require 'cl-lib)
(require 'subr-x)
(require 'request)
(require 'json)

(defvar claude-api-key nil) ; Anthropic Consoleから発行されるAPIキーを設定する
(defvar claude-confirmation-threshold 3000)
(defvar claude-endpoint "https://api.anthropic.com/v1/messages")
(defvar claude-api-version "2023-06-01")
(defvar claude-model "claude-sonnet-5")
(defvar claude-max-tokens 4096)

(cl-defun claude--confirm-send-long-string (&key retry)
  (let ((send-it-p
         (read-from-minibuffer
          (if retry
              "Please answer with \"yes\" or \"no\". [yes/no]: "
            (format "It's over %S characters, do you really want to send it? [yes/no]: "
                    claude-confirmation-threshold)))))
    (cond ((equal send-it-p "yes") t)
          ((equal send-it-p "no") nil)
          (t (claude--confirm-send-long-string :retry t)))))

(defun claude--effective-api-key ()
  (or claude-api-key
      (getenv "ANTHROPIC_API_KEY")))

(defun claude--language-name (lang)
  (cond ((equal lang "JA") "Japanese")
        ((equal lang "EN") "English")
        (t lang)))

(defun claude--system-prompt (source-lang target-lang)
  (format (concat "You are a professional translator. "
                  "Translate the user's text from %s to %s. "
                  "Return only the translated text. "
                  "Do not add explanations, quotes, labels, or Markdown.")
          (claude--language-name source-lang)
          (claude--language-name target-lang)))

(cl-defun claude-translate-internal (text source-lang target-lang success-callback)
  (let ((api-key (claude--effective-api-key)))
    (unless api-key
      (message "Error: claude not configured. Please set claude-api-key or ANTHROPIC_API_KEY.")
      (cl-return-from claude-translate-internal))

    (when (and (> (length text) claude-confirmation-threshold)
               (not (claude--confirm-send-long-string)))
      (cl-return-from claude-translate-internal))

    (let ((payload
           (json-encode
            `((model . ,claude-model)
              (max_tokens . ,claude-max-tokens)
              ;; (temperature . 0) ; deprecated for Sonnet5
              (system . ,(claude--system-prompt source-lang target-lang))
              (messages . [((role . "user")
                            (content . ,text))])))))
      (request claude-endpoint
        :type "POST"
        :headers `(("x-api-key" . ,api-key)
                   ("anthropic-version" . ,claude-api-version)
                   ("content-type" . "application/json"))
        :data payload
        :parser 'json-read
        :success success-callback
        :error (cl-function
                (lambda (&key error-thrown data &allow-other-keys)
                  (message "Error: %S %S" error-thrown data)))))))

(defun claude--content-block-text (block)
  (when (equal (cdr (assoc 'type block)) "text")
    (cdr (assoc 'text block))))

(defun claude--response-text (data)
  (let ((content (cdr (assoc 'content data))))
    (string-join
     (delq nil
           (mapcar #'claude--content-block-text
                   (if (vectorp content)
                       (append content nil)
                     content)))
     "\n")))

(cl-defun claude--output-to-messages (&key data &allow-other-keys)
  (let ((translated-text (claude--response-text data)))
    (kill-new translated-text)
    (message "%s" translated-text)))

(defun claude-ej (start end)
  (interactive "r")
  (let ((region (buffer-substring start end)))
    (claude-translate-internal region "EN" "JA" #'claude--output-to-messages)))

(defun claude-je (start end)
  (interactive "r")
  (let ((region (buffer-substring start end)))
    (claude-translate-internal region "JA" "EN" #'claude--output-to-messages)))

(defun claude--ja-char-p (char)
  (or (<= #x3041 char #x309f) ; hiragana
      (<= #x30a1 char #x30ff) ; katakana
      (<= #x4e01 char #x9faf) ; kanji
      ))

(defun claude--ja-string-p (str)
  (>= (cl-count-if #'claude--ja-char-p str) 3))

(defun claude-translate (start end)
  (interactive "r")
  (let ((region (buffer-substring start end)))
    (if (claude--ja-string-p region)
        (claude-translate-internal region "JA" "EN" #'claude--output-to-messages)
      (claude-translate-internal region "EN" "JA" #'claude--output-to-messages))))

(provide 'claude-translate)
```

init.el などからこのファイルを参照し、APIキーを書いたファイルを参照するようにして、キーバインドも設定しておく。

```elisp
;;; for claude-translate.el
(load (locate-user-emacs-file "site-lisp/claude-translate"))

(when (file-exists-p "~/.anthropic/credential.el")
  (load "~/.anthropic/credential.el"))

(global-set-key (kbd "C-c t") 'claude-translate)
```

`~/.anthropic/credential.el` はAPIキーを設定するのみのファイル。

```elisp
(setq claude-api-key "<YOUR_ANTHROPIC_API_KEY>")
```
