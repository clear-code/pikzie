.. -*- rst -*-

======
 NEWS
======

Pikzieの歴史

1.0.3: 2016-07-07
=================

修正
----

  * ``Ctrl-c`` でテストを途中終了できない問題を修正しました。
    [GitHub#24][Fujimoto Seijiさんがパッチ提供]

感謝
----

  * Fujimoto Seijiさん

1.0.2: 2016-07-02
=================

改良
----

  * README: ``test/run-test.py`` 実行時にパーミッションエラーになる場
    合の対応方法を追加。[GitHub#2][Yosuke Yasudaさんがパッチ提供]

  * README: リリース前のソースをインストールする方法を追加。
    [GitHub#3][Keita Watanabeさんがパッチ提供]

  * README: 説明の順番を改善。
    [GitHub#4][Keita Watanabeさんがパッチ提供]

  * Python 3対応。
    [GitHub#5][Yosuke Yasudaさんが報告]
    [GitHub#7][Shohei Kikuchiさんが報告]
    [GitHub#13][Yosuke Yasudaさんがパッチ提供]
    [GitHub#19][Fujimoto Seijiさんがパッチ提供]
    [GitHub#20][Fujimoto Seijiさんがパッチ提供]

  * コンソール出力: ``TERM`` の値が ``term-256color`` で終わるときはデ
    フォルトで色付きになるようにした。

  * README: オプションの指定方法を追加。
    [GitHub#10][kabayan55さんが提案]

修正
----

  * README: 見出しの位置を修正。
    [GitHub#12][Shohei Kikuchiさんがパッチ提供]

  * README: マークアップを修正。
    [GitHub#17][Shohei Kikuchiさんがパッチ提供]

  * ``pip install pikzie`` が失敗する問題を修正。
    [GitHub#18][Fujimoto Seijiさんがパッチ提供]

感謝
----

  * Yosuke Yasudaさん

  * Keita Watanabeさん

  * Shohei Kikuchiさん

  * kabayan55さん

  * Fujimoto Seijiさん

1.0.1: 2011-12-18
=================

パッケージ修正のみ。

1.0.0: 2011-12-18
=================

リポジトリをsourceforge.netから "GitHub
<https://github.com/clear-code/pikzie>"_ へ移行しました。

改良
----

  * subprocess対応。 [Tetsuya Morimotoさんが改良]
  * Python 3.2対応。
  * Python 2.5以下のサポートを終了。
  * 正規表現を表示するときに ``re.DOTALL`` を示すために
    ``d`` ではなく ``s`` を使うように変更。これは ``re.S``
    とあわせるためである。
  * ``--name`` と ``--test-case`` で 正規表現フラグに対応。
    ``/.../フラグ`` という書式で ``/.../i`` とすると大文字小
    文字を区別してマッチする。

修正
----

  * 同じファイルを2回読み込む問題を修正。
    [Hideo Hattoriさんが修正]
  * データ駆動テスト失敗時にテストデータの出力を失敗する問題を修正。
    [pikzie-users-ja:22] [Tetsuya Morimotoさんが修正]

感謝
----

  * Hideo Hattoriさん
  * Tetsuya Morimotoさん

0.9.7: 2010-05-24
=================

  * テスト読み込み時のテストモジュール名を正規化

0.9.6: 2010-05-20
=================

  * pikzie.utilsモジュールの追加
  * assert_existsの追加
  * assert_not_existの追加
  * 指定したディレクトリ以下すべてのテストスクリプト読み込みに対応
  * 必要な部分のみ色付けするように変更
  * assert_raise_callで例外のインスタンスも受け付けるように
    改良
  * データ駆動テストのサポート

0.9.5: 2009-07-23
=================

  * omitのサポート
  * 部分的にWindowsに対応

0.9.4: 2009-05-29
=================

  * 色付けモードではないときに出力に失敗する問題を修正
    [Hideo Hattoriさんによる報告]
  * 環境変数TERMの値の最後が"term-color"で終わっている場合も
    色付け可能な環境として扱うように変更

0.9.3: 2008-12-25
=================

  * sortedの誤検出を修正
  * assert_search_syslog_callでのメッセージ検出処理の改善

0.9.2: 2008-06-27
=================

  * diffの出力を改良
  * モジュールベースでのテスト作成をサポート

0.9.1: 2008-06-25
=================

  * デフォルトでは優先度モードを使用しないように変更
  * Python 2.5対応

0.9.0: 2008-03-31
=================

  * 優先度モード（--priority/--no-priorityオプション）の追加
  * LGPLv3 or laterを明記

0.8.0: 2008-03-24
=================

  * テスト結果をXML形式で出力する--xml-reportオプションの追加
  * diffの出力形式を改善
  * テスト結果の表示形式を改善

0.7.0: 2008-02-26
=================

  * 色付けされたトレースバックのサポート
  * assert_kernel_symbolの追加

0.6.0: 2008-02-25
=================

  * verboseモードでは連続する「通知」マークを圧縮

0.5.0: 2008-02-20
=================

  * --color-schemeオプションの追加

0.4.0: 2008-02-18
=================

  * assert_run_commandの追加
  * assert_search_syslog_callの追加
  * assert_open_fileの追加
  * assert_try_callの追加
  * assert_call_raise -> assert_raise_call
  * assert_call_nothing_raised -> assert_nothing_raised_call
  * pikzie.pretty_printモジュールの追加

0.3.0: 2008-02-14
=================

  * テストへのメタデータ付加機能の追加
  * screen環境下での自動色付けの有効化
  * pend, notifyの追加

0.2.0: 2008-01-31
=================

  * assert_call_nothing_raisedの追加
  * 自動テスト起動機能の追加
    （テスト起動スクリプト無しでもテストが走る）
  * コマンドライン引数からテストを実行するファイルを指定でき
    る機能の追加
  * --name, --test-caseオプションの追加
    （指定した名前のテスト・テストケースのみを実行する機能）
  * 色付けされた出力のサポート（--colorオプションの追加）
  * 詳細表示モードの追加（--verboseオプションの追加）
  * Python 2.3対応

0.1.0: 2008-01-28
=================

  * SF.netでの最初のリリース。
