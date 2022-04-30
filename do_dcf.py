# -*- coding:utf-8 -*-
import time
import serial
import binascii


li_open = ['FE 05 00 00 FF 00 98 35', 'FE 05 00 01 FF 00 C9 F5', 'FE 05 00 02 FF 00 39 F5', 'FE 05 00 03 FF 00 68 35',
           'FE 05 00 04 FF 00 D9 F4', 'FE 05 00 05 FF 00 88 34']
li_close = ['FE 05 00 00 00 00 D9 C5', 'FE 05 00 01 00 00 88 05', 'FE 05 00 02 00 00 78 05', 'FE 05 00 03 00 00 29 C5',
            'FE 05 00 04 00 00 98 04', 'FE 05 00 05 00 00 C9 C4']
li_status = ['FE 01 00 00 00 01 E9 C5', 'FE 01 00 01 00 01 B8 05', 'FE 01 00 02 00 01 48 05', 'FE 01 00 03 00 01 19 C5',
             'FE 01 00 04 00 01 A8 04', 'FE 01 00 05 00 01 F9 C4']



def get_status(com,operate_dcf):

    get_result = 0
    try:
        ser = serial.Serial("COM" + str(com), 9600, 8)

        if ser.isOpen():

            result = ser.write(bytes.fromhex(operate_dcf))

            if result != 0:

                times = 0
                while 1:

                    len_return_data = ser.inWaiting()
                    time.sleep(0.01)
                    times += 1

                    print(len_return_data)
                    if len_return_data != 0:
                        read_data = ser.read(len_return_data)
                        get_result = str(binascii.b2a_hex(read_data))[2:-1]
                        break
                    if times > 50:
                        break
        ser.close()

    except:
        print('open_serial_error')

    return get_result


def open(com,position):

    operate_dcf=li_open[position]

    len_return_data = 0

    try:
        ser = serial.Serial("COM" + str(com), 9600, 8)

        if ser.isOpen():

            result = ser.write(bytes.fromhex(operate_dcf))

            if result!=0:

                times = 0
                while 1:

                    len_return_data = ser.inWaiting()
                    time.sleep(0.01)
                    times += 1

                    print(len_return_data)
                    if len_return_data!= 0:
                        break
                    if times > 50:
                        break
        ser.close()

    except:
        print('open_serial_error')

    if len_return_data!=0:

        print("chazhuangtai")

        getstatus_dcf=li_status[position]

        read_data=get_status(com,getstatus_dcf)

        if read_data != 0:
            if read_data != 'fe010100619c':
                return 1
            else:
                return 0

        else:
            return 0

    else:
        return 0

def close(com,position):

    operate_dcf = li_close[position]

    len_return_data = 0
    try:

        ser = serial.Serial("COM" + str(com), 9600, 8)

        if ser.isOpen():

            result = ser.write(bytes.fromhex(operate_dcf))

            if result != 0:

                times = 0
                while 1:

                    len_return_data = ser.inWaiting()
                    time.sleep(0.01)
                    times += 1

                    print(len_return_data)
                    if len_return_data != 0:
                        break
                    if times > 50:
                        break
        ser.close()

    except:
        print('open_serial_error')

    if len_return_data != 0:

        getstatus_dcf = li_status[position]
        read_data = get_status(com, getstatus_dcf)

        if read_data != 0:
            if read_data == 'fe010100619c':
                return 1
            else:
                return 0

        else:
            return 0
    else:
        return 0

if __name__=='__main__':
    open()