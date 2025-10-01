/* include/autoconf.h */
#ifndef __AUTOCONF_H__
#define __AUTOCONF_H__

/* 芯片/平台 */
#define CONFIG_CHIP_A_CUT              1
#define CONFIG_PLATFORM_8721D          1
#define CONFIG_CHIP_ID                 0x8721

/* 映像型態 */
#define CONFIG_BUILD_RAM               1
#define CONFIG_BUILD_ROM               0

/* OS */
#define CONFIG_CMSIS_OS                1
#define CONFIG_FREERTOS                1
#define CONFIG_TOOLCHAIN_ARM_GCC       1

/* TrustZone 關閉（避免 mcmse 相關警告/需求）*/
#define CONFIG_TRUSTZONE               0
#define CONFIG_TRUSTZONE_EN            0
#define CONFIG_AMEBAD_TRUSTZONE        0

/* 網路/無線（先關，有需要再逐步打開） */
#define CONFIG_WIFI_EN                 1
#define CONFIG_WLAN                    1
#define CONFIG_LWIP_LAYER              1

/* 其他常見周邊先關 */
#define CONFIG_BT                      1
#define CONFIG_AUDIO                   0
#define CONFIG_USB_OTG                 0
#define CONFIG_SDIO_DEVICE             0

#endif /* __AUTOCONF_H__ */
