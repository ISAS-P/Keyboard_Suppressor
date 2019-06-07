import pyaudio 
import datetime
from pyhooked import Hook, KeyboardEvent
import threading

key_flag = 0 #キーボード打鍵判別用グローバル変数

def select_device():
    INPUT_DEVICE_INDEX=0
    OUTPUT_DEVICE_INDEX=0
    WAIT = 0
    #CHUNK = 0
    
    audio = pyaudio.PyAudio()
    # 音声デバイス毎のインデックス番号を一覧表示
    print("入力デバイス")
    for x in range(0, audio.get_device_count()): 
        device = audio.get_device_info_by_index(x)
        if(device['maxInputChannels']>0):#入力デバイスを抽出
            device_num = device['index']
            device_name = device['name']
            print("Num:{0},Name:{1}".format(device_num,device_name))
    print("\n")
    print("入力デバイスのNumを選択してください")
    INPUT_DEVICE_INDEX=input()
    print("\n")
        
    print("出力デバイス")
    for x in range(0, audio.get_device_count()): 
        device = audio.get_device_info_by_index(x)   
        if(device['maxOutputChannels']>0):#出力デバイスを抽出
            device_num =device['index'] 
            device_name =device['name']
            print("Num:{0},Name:{1}".format(device_num,device_name))
    print("\n")
    print("出力デバイスのNumを選択してください")
    OUTPUT_DEVICE_INDEX=input()
    print("\n")
    print("キー打鍵後の待ち時間[秒]を入力してください")
    WAIT=input()
    print("\n")
    
    return INPUT_DEVICE_INDEX,OUTPUT_DEVICE_INDEX,WAIT
    
def handle_events(args):
    global key_flag
    if isinstance(args, KeyboardEvent):
        if(args.event_type=="key down"):
            key_flag = 1 #key_flagを1に→打鍵あり
        else:
            key_flag = 0 #key_flagを0に→打鍵なし

def keyboard_check():
    hk = Hook()
    hk.handler = handle_events
    thread = threading.Thread(target=hk.hook)
    thread.setDaemon(True)
    thread.start()

def main():
    global key_flag
    
    print("Keyboard_Suppressor ver1.0")
    print("Developed by ISAS-P")
    print("\n")
    
    Input_Device_Index,Output_Device_Index,wait = select_device()
    Input_Device_Index = int(Input_Device_Index)
    Output_Device_Index = int(Output_Device_Index)
    wait = float(wait)
    
    print("終了時はウィンドウの閉じるボタンか、Ctrl+Cで終了してください")
    keyboard_check()
    
    CHUNK=1024*2
    RATE=44100
    Atten_Rate = 0.0 #音声減衰率→将来的に使うかも
    
    wait = wait + ((1/RATE)* CHUNK)
    
    p=pyaudio.PyAudio()
    
    stream=p.open(format = pyaudio.paInt16,
                  channels = 1,
                  rate = RATE,
                  frames_per_buffer = CHUNK,
                  input_device_index = Input_Device_Index,
                  input = True,
                  output_device_index = Output_Device_Index,
                  output = True) # inputとoutputを同時にTrueにする
                  
    input = stream.read(CHUNK)
    while stream.is_active():
        #ここから処理記述を開始
        if (key_flag!=0): #打鍵が検出されたら
            now_time = datetime.datetime.now()#現在時刻取得
            target_time = now_time + datetime.timedelta(seconds=wait)#ターゲット時刻を設定_wait秒後
            while(target_time>now_time):#現在時刻が目標時間に到達しない限り
                before_input = input
                input = stream.read(CHUNK)#音声は読み込むが、出力はしない
                now_time = datetime.datetime.now()#現在時刻取得
                if (key_flag!=0):#複数回打鍵があれば
                    target_time =now_time + datetime.timedelta(seconds=wait)#ターゲット時刻を現在時刻からwait秒後に変更
                
        else:#打鍵が検出されないなら
            before_input = input
            input = stream.read(CHUNK)#音声入力
            output = stream.write(before_input)#音声を出力
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\n")
    print("終了しました")
    sys.exit()
    
if __name__ == "__main__":
    main()