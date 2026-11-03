import serial
import time
import sys

class KondoServo :
    def __init__(self,port):
        try:
            self.krs = serial.Serial(port, baudrate=115200, parity=serial.PARITY_EVEN, timeout=0.5)
        except Exception as e:
            print(e)
            input("press any key to exit")
            sys.exit()


    #ID番号で指定したサーボに角度を指定して動作します
    def krs_setPos_CMD(self,servo_id, pos):
        
        txCmd = [0x80 | servo_id,   #ポジションコマンド0ｘ80にＩＤ番号を足し合わせてヘッダにします
                pos >> 7 & 0x7f,   #ポジションデータを2バイトに分けます
                pos & 0x7f]
    
        #コマンドを送信
        self.krs.write(txCmd)
        
        #サーボからの返事を受け取る
        rxCmd = self.krs.read(6)
        #もしリスト何になにも入っていなかったら正常に受信できていないと判断    
        if len(rxCmd) == 0:
            return False,0

        #問題なければ返事を返す        
        else:
            
            #受け取った2Byteの現在位置を1バイトのデータにまとめて戻り値にします
            #※この現在位置は、サーボがポジションを受け取って動き出す前の現在位置です
            #return True, (rxCmd[4] << 7) + rxCmd[5]
            return True,0



#サーボを脱力した状態にします    
    def krs_setFree_CMD(self,servo_id):
        
        #ポジション0送信すると脱力します
        bl, Value = self.krs_setPos_CMD(servo_id, 0)
        return bl, Value
        

    #サーボのストレッチ、スピード、電流値、温度を読み出します
    #※現在位置を取得する場合は、getPos関数を使用してください
    #※EEPROM(sc:0x00)の読み出しには対応していません
    #※KRS-3301/3302は温度、電流回路が実装されていません
    def krs_getValue_CMD(self,servo_id, sc):
    
        txCmd = [0xA0 | servo_id,   #読み出しコマンド0xA0にＩＤ番号を足し合わせてヘッダにします
                sc]                #sc（サブコマンド）により、読み出すパラメータを指定します
    
        #コマンドを送信
        self.krs.write(txCmd)

        #サーボからの返事を受け取る
        rxCmd = self.krs.read(5)
        
        #もしリスト何になにも入っていなかったら正常に受信できていないと判断    
        if len(rxCmd) == 0:
            return False, 0

        #問題なければ返事を返す
        else:
            return True, rxCmd[4]



    #サーボの現在位置を読み出します
    #サブコマンド0ｘ05により現在位置を読み出すことができますが、このコマンドはＩＣＳ3.6のみ対応しています
    #ICS3.5をご利用の場合は、getPos35関数を使用してください
    def krs_getPos36_CMD(self,servo_id):
    
        txCmd = [0xA0 | servo_id,   #読み出しコマンド0xA0にＩＤ番号を足し合わせてヘッダにします
                0x05]              #sc（サブコマンド）により、現在位置を読み出します
    
        #コマンドを送信
        self.krs.write(txCmd)

        #サーボからの返事を受け取る
        rxCmd = self.krs.read(6)
        
        #もしリスト何になにも入っていなかったら正常に受信できていないと判断    
        if len(rxCmd) == 0:
            return False, 0

        #問題なければ返事を返す        
        else:
            
            #読み出した2バイトのデータを１つのデータにまとめて戻り値とします
            return True, (rxCmd[4] << 7) + rxCmd[5]


    #サーボの現在位置を読み出します
    #ICS3.5は現在位置を取得するコマンドが実装されていないため
    #ポジションコマンドを送信した際に返事で取得できる角度を利用します
    def krs_getPos35_CMD(self,servo_id):
    
        #ポジションコマンドの戻り値で現在位置を取得するため、ポジション0でサーボから戻り値を取得する
        bl, Value = self.krs_setPos_CMD(servo_id, 0)
            
        #フリー状態のサーボに取得したポジションと同じポジションを送信し、トルクオン状態に戻します
        bl, Value = self.krs_setPos_CMD(servo_id, Value)
        
        return bl, Value



    #サーボのストレッチ、スピード、電流制限値、温度制限値を書き換えます
    #※EEPROM(sc:0x00)の書き込みには対応していません
    def krs_setValue(self,servo_id, sc, Value):
        
        #サブコマンドがEEPROM(sc:0x00)の場合は処理を停止する
        if (sc == 0x00) :
            return False
        
        txCmd = [0xC0 | servo_id,   #書き込みコマンド0ｘC0にＩＤ番号を足し合わせてヘッダにします
                sc,                #sc（サブコマンド）により、書き込み先を指定します
                Value]             #書き込むパラメータ

        #コマンドを送信
        self.krs.write(txCmd)

        #サーボからの返事を受け取る
        rxCmd = self.krs.read(6)
        
        #もしリスト何になにも入っていなかったら正常に受信できていないと判断    
        if len(rxCmd) == 0:
            return False

        #問題なければ返事を返す
        else:
            
            #サーボからの返事で書き込んだデータが返ってきます。指定したデータと合っているか確認します
            if rxCmd[5] == Value:
                return True
            
            else:
                return False



    #サーボのIDを読み出します
    #ホストとサーボを1対1の状態で使用してください
    #IDは複数のサーボを同時に接続して読み込むことはできません
    def krs_getID_CMD(self):
        
        txCmd = [0xFF,  #IDコマンド0ｘFF
                0x00,  #ID読み出しのサブコマンド0x00を3回送ります
                0x00,
                0x00]

        #コマンドを送信
        self.krs.write(txCmd)

        #サーボからの返事を受け取る
        rxCmd = self.krs.read(5)
        
        #もしリスト何になにも入っていなかったら正常に受信できていないと判断    
        if len(rxCmd) == 0:
            return False, 0

        #問題なければ返事を返す        
        else:
            
            #読み出したからIDのみを残して戻り値とします
            return True, rxCmd[4] & 0x1F



