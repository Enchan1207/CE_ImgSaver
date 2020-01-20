# DBのキュー処理

## DBAccess.pyの問題
クラス`DBAccess`の処理はシングルスレッドによる使用を想定して実装されており、マルチスレッドで`DBAccess`をインスタンス化すると以下のようなエラーが発生します:

    SQLite objects created in a thread can only be used in that same thread. 
    The object was created in thread id XXXXXX and this is thread id YYYYYY.

これは`DBAccess.py`内でインポートしている`sqlite`モジュールの仕様に起因するものであり、このままでは複数スレッドのDBアクセスを捌くことができません。  

## DBQueue.pyによるキュー処理
この問題を、今回はクラス`DBQueue`を実装することで解決しました。  
`DBQueue`では複数のスレッドから行われるDBアクセスを`enQueue`関数によって`rqQueue`に一時保存します。  
この関数は`DBAccess::exec`と同じように扱うことができます。  
デーモンスレッドに`deQueue`関数を処理させることで、実際のDBアクセスはデーモンスレッドのみが行うようになり、  
実質「シングルスレッドを保ったままマルチスレッドによるDBアクセスを捌く」という動作になります。  
`deQueue`の待機は`enQueue`の引数に渡された`threading.Event`でも行えます。  