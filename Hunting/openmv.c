/* �Թ�hunting.py��v2.0_blob.py */

#include "openmv.h"
#include "inv_mpu.h"
#include "inv_mpu_dmp_motion_driver.h"
#include "motor.h"
#include "mpu6050.h"
#include "oled.h"
#include "pid.h"
#include "stdio.h"
#include "usart.h"
#include <string.h>

static int8_t Cx = 0, Cy = 0, Cw = 0, Ch = 0;
float jiaodu;
extern tPid pidMPU6050YawMovement; //����6050ƫ���� ������̬���Ƶ�PID
extern float Motor1Speed;
extern float Motor2Speed;
extern float pitch, roll, yaw;         // ������ ����� �����
extern float g_fMPU6050YawMovePidOut;  //��̬PID�������
extern float g_fMPU6050YawMovePidOut1; //��һ������������
extern float g_fMPU6050YawMovePidOut2; //��һ������������
uint8_t Usart2String[50];

void Openmv_Receive_Data(int16_t com_data) {
  //  OLED_ShowNum(20,4,7,1,2);
  uint8_t i;
  static uint8_t RxCounter1 = 0; //����
  static uint16_t RxBuffer1[10] = {0};
  static uint8_t RxState = 0;
  static uint8_t RxFlag1 = 0;
  //    OLED_ShowNum(20,4,com_data,4,2);
  if (RxState == 0 && com_data == 0x2c) // 0x2c֡ͷ
  {
    //                    OLED_ShowNum(20,4,1,3,2);
    RxState = 1;
    RxBuffer1[RxCounter1++] = com_data;
  }

  else if (RxState == 1 && com_data == 0x12) // 0x12֡ͷ
  {
    RxState = 2;
    RxBuffer1[RxCounter1++] = com_data;
  } else if (RxState == 2) {

    RxBuffer1[RxCounter1++] = com_data;
    if (RxCounter1 >= 10 || com_data == 0x5B) // RxBuffer1��������,�������ݽ���
    {
      RxState = 3;
      RxFlag1 = 1;

      Cx = RxBuffer1[RxCounter1 - 5];
      Cy = RxBuffer1[RxCounter1 - 4];
      Cw = RxBuffer1[RxCounter1 - 3];
      Ch = RxBuffer1[RxCounter1 - 2];

      //                        OLED_ShowNum(0,4,Cx,1,4);
      //                        OLED_ShowNum(0,4,Ch,1,4);
      sprintf((char *)Usart2String, "Cx:%dCy:%dCw:%d\r\n", Cx, Cy,
              Cw); //��ʾ�������ת�� ��λ��ת/��
      HAL_UART_Transmit(&huart3, (uint8_t *)Usart2String,
                        strlen((const char *)Usart2String), 50);
      Cx -= 40;
      if (Cw)
        Cy = -Cy;
      jiaodu = (Cx + Cy) / 30.0;
      motorPidSetSpeed(-1 + jiaodu, -1 - jiaodu);
    }
  }

  else if (RxState == 3) //����Ƿ���ܵ�������־
  {
    if (RxBuffer1[RxCounter1 - 1] == 0x5B) {

      RxFlag1 = 0;
      RxCounter1 = 0;
      RxState = 0;

    } else //���մ���
    {
      RxState = 0;
      RxCounter1 = 0;
      for (i = 0; i < 10; i++) {
        RxBuffer1[i] = 0x00; //�����������������
      }
    }
  }

  else //�����쳣
  {
    RxState = 0;
    RxCounter1 = 0;
    for (i = 0; i < 10; i++) {
      RxBuffer1[i] = 0x00; //�����������������
    }
  }
}
