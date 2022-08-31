import time # デバッグ用
import wrapt_timeout_decorator

# デコレータでタイムアウトの秒数を設定します
@wrapt_timeout_decorator.timeout(dec_timeout=3.5)
def func(number, text):
    """『長い時間がかかるかもしれない関数』"""

    # (デバッグ) 長い時間待機してみる。
    time.sleep(number)
    z = f'{number} 秒のスリープ OK。text="{text}"'

    return z

import datetime # デバッグ用
import os # デバッグ用
import traceback # デバッグ用
import multiprocessing


def main():
    """メイン関数"""
    print('start\n')

    # 使いたい引数のリストを作ります。
    args_list = [
        [1, 'あ'],
        [2, 'い'],
        [3, 'う'],
        [4, 'え'],
        [5, 'お'],
        ]

    print('実行中...')

    processes = 1 # シングルプロセス処理
    # processes = 3 # マルチプロセス処理

    if processes == 1:
        print(f'=== シングルプロセス処理 (processes={processes}) ===')
        results = []
        for args in args_list:
            result = proc(*args)
            results.append(result)
    elif processes >= 2:
        print(f'=== マルチプロセス処理 (processes={processes}) ===')
        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.map(mp_proc_wrapper, args_list)

    print('\n結果を表示します。')
    for result in results:
        print(result)

    print('\nend')
    return


def mp_proc_wrapper(args):
    """
    (シングルプロセス処理の時は必要無いです)
    マルチプロセス処理の時に引数をアンパックして渡す関数。
    """
    return proc(*args)


def proc(number, text):
    """自作の処理"""

    result = None

    # (デバッグ) 現在の時刻を取得します。
    t1 = datetime.datetime.now()

    # (デバッグ) 親プロセスのプロセス ID を取得します。
    ppid = f'PPID={os.getppid()}' # the parent's process id.

    # (デバッグ) 現在のプロセスのプロセス ID を取得します。
    pid = f'PID={os.getpid()}' # the current process id.

    try:
        #『長い時間がかかるかもしれない関数』を実行します。
        result = func(number, text)
    except TimeoutError as e:
        # タイムアウトしました。
        result = e.__class__.__name__
        print(traceback.format_exception_only(type(e), e)[0].rstrip('\n'))
        print(f'func(number={number}, text="{text}") Error')
    else:
        # 何のエラーも起きませんでした。
        print(f'func(number={number}, text="{text}") OK')

    # (デバッグ) 経過時間を計算します。
    elapsed_time = (datetime.datetime.now() - t1).total_seconds()
    total_seconds = '%.3f 秒' % elapsed_time

    return (number, text, total_seconds, ppid, pid, result)


if __name__ == "__main__":
    main()