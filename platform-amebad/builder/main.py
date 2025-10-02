import os
from SCons.Script import DefaultEnvironment, AlwaysBuild, Alias
import glob
import subprocess
import re

env = DefaultEnvironment() # SDK 與 Toolchain 路徑

sdk_dir = os.path.join(env.subst("$PROJECT_DIR"), ".pio", "framework-amebad-rtos-d")

if not os.path.exists(sdk_dir):
    print(">>> Cloning AmebaD SDK ...")
    subprocess.check_call([
        "git", "clone", "--depth=1",
        "https://github.com/Ameba-AIoT/ameba-rtos-d.git",
        sdk_dir
    ])

# 讀取開關：platformio.ini 可設 build_flags = -DTRUSTZONE=1
USE_TZ = int(env.GetProjectOption("trustzone") or
             os.environ.get("CONFIG_TRUSTZONE", "0") or
             ("TRUSTZONE" in (env.get("CPPDEFINES") or []) and "1") or
             0)

project_km0_dir = os.path.join(env.subst("$PROJECT_DIR"), "src_km0")
project_km4_dir = os.path.join(env.subst("$PROJECT_DIR"), "src_km4")

asdk_km0_dir = os.path.join(sdk_dir, "project/realtek_amebaD_va0_example/GCC-RELEASE/project_lp/asdk")
asdk_km4_dir = os.path.join(sdk_dir, "project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp/asdk")

toolchain = env.PioPlatform().get_package_dir("toolchain-gccarmnoneeabi")

gcc = os.path.join(toolchain, "bin", "arm-none-eabi-gcc")
ld = os.path.join(toolchain, "bin", "arm-none-eabi-ld")
objcopy = os.path.join(toolchain, "bin", "arm-none-eabi-objcopy")
fromelf = os.path.join(toolchain, "bin", "arm-none-eabi-objcopy")
strip = os.path.join(toolchain, "bin", "arm-none-eabi-strip")

utility_km0_dir = os.path.join(asdk_km0_dir, "gnu_utility")
utility_km4_dir = os.path.join(asdk_km4_dir, "gnu_utility")

prepend_sh_km0 = os.path.join(utility_km0_dir, "prepend_header.sh")
prepend_sh_km4 = os.path.join(utility_km4_dir, "prepend_header.sh")

prepend_ota_sh_km0 = os.path.join(utility_km0_dir, "prepend_ota_header.sh")
prepend_ota_sh_km4 = os.path.join(utility_km4_dir, "prepend_ota_header.sh")

pad_sh_km0 = os.path.join(utility_km0_dir, "pad.sh")
pad_sh_km4 = os.path.join(utility_km4_dir, "pad.sh") 

# Windows 可執行檔（若有的話） 
imgpad_exe_km0 = os.path.join(utility_km0_dir, "imgpad.exe") 
imgpad_exe_km4 = os.path.join(utility_km4_dir, "imgpad.exe") 

checksum_exe_km0 = os.path.join(utility_km0_dir, "checksum.exe") 
checksum_exe_km4 = os.path.join(utility_km4_dir, "checksum.exe") 

# build 目錄 
build_dir = os.path.join(env.subst("$BUILD_DIR"), "amebad")
if not os.path.exists(build_dir): 
    os.makedirs(build_dir) 

boot_km0_src = [
    os.path.join(sdk_dir, "component/soc/realtek/amebad/bootloader/boot_flash_lp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/bootloader/boot_ram_lp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_bootcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_wdg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_clk.c"),
]

boot_km4_src = [
    os.path.join(sdk_dir, "component/soc/realtek/amebad/bootloader/boot_ram_hp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/bootloader/boot_flash_hp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_bootcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/bootloader/boot_trustzone_hp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dhp_boot_trustzonecfg.c"),
]

# KM0 sources/inc 
km0_src = [
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/low_level_io.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/monitor_lp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/rtl_trace.c"),
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/shell_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/rom/monitor_rom.c"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_adc.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_bor.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_captouch.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_comparator.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_efuse.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_flash_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_i2c.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_ipc_api.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_keyscan.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_pll.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_qdec.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_rtc.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_sgpio.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_tim.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_uart.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_wdg.c"),
    
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_app_start.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_clk.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_cpft.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_flashclk.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_km4.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_pinmap.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_simulation.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_startup.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_lp/rtl8721dlp_system.c"),
    
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_bootcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_ipccfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_wificfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dlp_flashcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dlp_intfcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dlp_pinmapcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dlp_sleepcfg.c"),

    #os.path.join(sdk_dir, "component/soc/realtek/amebad/misc/rtl8721d_ota.c"),

    os.path.join(sdk_dir, "component/os/freertos/freertos_backtrace_ext.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_heap5_config.c"),

    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/list.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/queue.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/tasks.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/timers.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/croutine.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/event_groups.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/stream_buffer.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/portable/MemMang/heap_5.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/portable/GCC/ARM_CM0/port.c"),
] 

km0_inc = [ 
    os.path.join(sdk_dir, "component/common/api"),
    os.path.join(sdk_dir, "component/common/api/platform"),
    os.path.join(sdk_dir, "component/common/network/ssl/ssl_ram_map/rom"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/include"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/hal/config"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/include"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/touch_key"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/xmodem"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/cmsis"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/include"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usb_otg/device"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usb_otg/host"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/swlib/include"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/swlib/string"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/misc"),

    os.path.join(sdk_dir, "component/os/os_dep/include"),
    os.path.join(sdk_dir, "component/os/freertos"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/include"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/portable/GCC/ARM_CM0"),
] 

# KM4 sources/inc 
km4_src = [ 
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/hal/config/audio_hw_config.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/low_level_io.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/monitor_hp.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/rtl_trace.c"),
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/ram/shell_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/rom/monitor_rom.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/rom/shell_rom.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/touch_key/touch_key.c"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_aes_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_aes_rom.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_chacha_poly1305.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_crypto_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_des_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_des_rom.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_md5.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/crypto/rtl8721dhp_sha.c"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_adc.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_bor.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_captouch.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_comparator.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_efuse.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_flash_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_gdma_memcpy.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_gdma_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_i2c.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_ipc_api.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_ir.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_keyscan.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_pll.c"),
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_qdec.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_ram_libc.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_rtc.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_sgpio.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_tim.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_uart.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_common/rtl8721d_wdg.c"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_app_start.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_audio.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_clk.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_cpft.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_i2s.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_lcdc.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_ota_ram.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_sd.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_sdio.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_sdio_host.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_simulation.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_ssi.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_startup.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/ram_hp/rtl8721dhp_system.c"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_bootcfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_ipccfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721d_wificfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dhp_boot_trustzonecfg.c"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usrcfg/rtl8721dhp_intfcfg.c"),
    
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/img3/boot_img3.c"),
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/img3/rtl8721dhp_crc.c"),
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/img3/secure_efuse.c"),
    #os.path.join(sdk_dir, "component/soc/realtek/amebad/img3/secure_src.c"),

    #os.path.join(sdk_dir, "component/soc/realtek/amebad/misc/rtl8721d_ota.c"),

    os.path.join(sdk_dir, "component/os/freertos/cmsis_os.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_backtrace_ext.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_heap5_config.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_service.c"),

    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/list.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/queue.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/tasks.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/timers.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/croutine.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/event_groups.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/stream_buffer.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/portable/MemMang/heap_5.c"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/portable/GCC/ARM_CM4F/port.c"),

    os.path.join(sdk_dir, "component/os/os_dep/device_lock.c"),
    os.path.join(sdk_dir, "component/os/os_dep/osdep_service.c"),
    os.path.join(sdk_dir, "component/os/os_dep/psram_reserve.c"),
    os.path.join(sdk_dir, "component/os/os_dep/tcm_heap.c"),

    #os.path.join(sdk_dir, "component/common/api/wifi_interactive_mode.c"),
    os.path.join(sdk_dir, "component/common/api/lwip_netconf.c"),
    
    os.path.join(sdk_dir, "component/common/api/wifi/rtw_wpa_supplicant/wpa_supplicant/wifi_eap_config.c"),
    os.path.join(sdk_dir, "component/common/api/wifi/wifi_conf.c"),
    os.path.join(sdk_dir, "component/common/api/wifi/wifi_ind.c"),
    os.path.join(sdk_dir, "component/common/api/wifi/wifi_promisc.c"),
    os.path.join(sdk_dir, "component/common/api/wifi/wifi_simple_config.c"),
    os.path.join(sdk_dir, "component/common/api/wifi/wifi_util.c"),

    os.path.join(sdk_dir, "component/common/drivers/wlan/realtek/src/osdep/lwip_intf.c"),
    
    #os.path.join(sdk_dir, "component/common/api/network/src/ping_test.c"),
    os.path.join(sdk_dir, "component/common/api/network/src/ttcp.c"),
    os.path.join(sdk_dir, "component/common/api/network/src/wlan_network.c"),

    os.path.join(sdk_dir, "component/common/network/ssl/ssl_ram_map/ssl_ram_map.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/ssl_ram_map/rom/rom_ssl_ram_map.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/ssl_wrapper/ssl_wrapper.c"),

    os.path.join(sdk_dir, "component/common/network/dhcp/dhcps.c"),

    os.path.join(sdk_dir, "component/common/example/cm_backtrace/example_cm_backtrace.c"),

    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek/freertos/br_rpt_handle.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek/freertos/bridgeif_fdb.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek/freertos/bridgeif.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek/freertos/ethernetif.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek/freertos/sys_arch.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/api_lib.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/api_msg.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/err.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/netbuf.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/netdb.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/netifapi.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/sockets.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/api/tcpip.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/def.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/dns.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/inet_chksum.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/init.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ip.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/mem.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/memp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/netif.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/pbuf.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/raw.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/stats.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/tcp_in.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/tcp_out.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/tcp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/timeouts.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/udp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/autoip.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/dhcp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/etharp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/icmp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/igmp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/ip4_addr.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/ip4_frag.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv4/ip4.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/dhcp6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/ethip6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/icmp6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/inet6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/ip6_addr.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/ip6_frag.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/ip6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/mld6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/core/ipv6/nd6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ethernet.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ethernetif.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/lowpan6.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/slipif.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/auth.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/ccp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/chap_ms.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/chap-md5.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/chap-new.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/demand.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/eap.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/eui64.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/fsm.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/ipcp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/ipv6cp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/lcp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/lwip_ecp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/magic.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/mppe.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/multilink.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/ppp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/pppapi.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/pppoe.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/pppol2tp.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/pppos.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/upap.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/utils.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/vj.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/polarssl/arc4.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/polarssl/des.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/polarssl/md4.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/polarssl/md5.c"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/netif/ppp/polarssl/sha1.c"),
    
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/analogin_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/captouch_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/dma_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/efuse_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/flash_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/gpio_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/gpio_irq_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/i2c_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/i2s_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/keyscan_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/lcdc_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/nfc_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/pinmap_common.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/pinmap.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/port_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/pwmout_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/rtc_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/serial_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/sleep.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/spdio_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/spi_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/sys_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/timer_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/us_ticker_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/us_ticker.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/wait_api.c"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d/wdt_api.c"),
    
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/mbedtls_rom_test.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/aes.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/aesni.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/arc4.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/asn1parse.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/asn1write.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/base64.c"),
    #os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/bignum.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/blowfish.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/camellia.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ccm.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/certs.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/cipher_wrap.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/cipher.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/cmac.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ctr_drbg.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/debug.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/des.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/dhm.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ecdh.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ecdsa.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ecjpake.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ecp_curves.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ecp_ram.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/entropy_poll.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/entropy.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/error.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/havege.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/hmac_drbg.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/md_wrap.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/md.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/md2.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/md4.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/md5.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/memory_buffer_alloc.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/net_sockets.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/oid.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/padlock.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pem.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pk_wrap.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pk.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pkcs5.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pkcs11.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pkcs12.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pkparse.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/pkwrite.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/platform.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ripemd160.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/rsa.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/sha1.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/sha256.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/sha512.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_cache.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_ciphersuites.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_cli.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_cookie.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_srv.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_ticket.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/ssl_tls.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/threading.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/timing.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/version_features.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/version.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509_create.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509_crl.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509_crt.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509_csr.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509write_crt.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/x509write_csr.c"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library/xtea.c"),
    #os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library_s/mbedtls_ext_nsc.c"),
    #os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/library_s/mbedtls_nsc.c"),
] 

km4_inc = [
    os.path.join(sdk_dir, "component/common/api"),
    os.path.join(sdk_dir, "component/common/api/network/include"),
    os.path.join(sdk_dir, "component/common/api/platform"),

    os.path.join(sdk_dir, "component/common/api/wifi"),
    os.path.join(sdk_dir, "component/common/api/wifi/rtw_wpa_supplicant/src"),
    
    os.path.join(sdk_dir, "component/common/drivers/wlan/realtek/include"),
    os.path.join(sdk_dir, "component/common/drivers/wlan/realtek/src/osdep"),
    os.path.join(sdk_dir, "component/common/drivers/wlan/realtek/wlan_ram_map/rom"),

    os.path.join(sdk_dir, "component/common/network"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/port/realtek/freertos"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/include"),
    os.path.join(sdk_dir, "component/common/network/lwip/lwip_v2.0.2/src/include/lwip"),
    os.path.join(sdk_dir, "component/common/network/ssl/ssl_ram_map/rom"),
    os.path.join(sdk_dir, "component/common/network/ssl/mbedtls-2.4.0/include"),

    os.path.join(sdk_dir, "component/common/mbed/api"),
    os.path.join(sdk_dir, "component/common/mbed/hal"),
    os.path.join(sdk_dir, "component/common/mbed/hal_ext"),
    os.path.join(sdk_dir, "component/common/mbed/targets/hal/rtl8721d"),

    os.path.join(sdk_dir, "component/common/test"),

    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/hal/config"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/monitor/include"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/touch_key"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/app/xmodem"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/cmsis"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/include"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usb_otg/device"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/fwlib/usb_otg/host"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/swlib/include"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/swlib/string"),
    os.path.join(sdk_dir, "component/soc/realtek/amebad/misc"),

    os.path.join(sdk_dir, "component/os/os_dep/include"),
    os.path.join(sdk_dir, "component/os/freertos"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/include"),
    os.path.join(sdk_dir, "component/os/freertos/freertos_v10.2.0/Source/portable/GCC/ARM_CM4F"),
] 

# .a libraries (wifi_fw, pmc_lp, rom.a) 
extra_libs_km0 = [ "_pmc_lp", "_wifi_fw" ]
extra_libs_km4 = [ "_pmc_hp", "_wlan", "_wlan_lp", "_wlan_lt", "_wlan_mp", "_wps" ] 

def norm_unix(path):
    return path.replace("\\", "/")

def collect_sources(root, exts=(".c", ".cpp")):
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(root, "**", "*" + ext), recursive=True))
    return files

def _mk_objs(envx, srcs, obj_root): 
    objs = [] 
    for s in srcs: 
        rel = os.path.relpath(s, sdk_dir).replace("\\", "/") 
        obj = os.path.join(obj_root, rel) + ".o"
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        objs.append(envx.Object(target=obj, source=s)) 
    return objs

toolbin = os.path.join(toolchain, "bin")

def set_xtools(e):
    e.Replace( CC=os.path.join(toolbin, "arm-none-eabi-gcc"),
              CXX=os.path.join(toolbin, "arm-none-eabi-g++"),
              AS=os.path.join(toolbin, "arm-none-eabi-gcc"),
              AR=os.path.join(toolbin, "arm-none-eabi-ar"),
              RANLIB=os.path.join(toolbin, "arm-none-eabi-ranlib"),
              OBJCOPY=os.path.join(toolbin, "arm-none-eabi-objcopy"),
              OBJDUMP=os.path.join(toolbin, "arm-none-eabi-objdump"),
              NM=os.path.join(toolbin, "arm-none-eabi-nm"),
              SIZE=os.path.join(toolbin, "arm-none-eabi-size"), ) 
    
    # 保險：把 toolchain/bin 也塞進 PATH（有些外部腳本/工具會用到） 
    e.PrependENVPath("PATH", toolbin) 

def apply_ini_build_flags(envx): 
    raw = envx.GetProjectOption("build_flags") or ""
    flags = envx.ParseFlags(raw)
    envx.AppendUnique( CPPDEFINES = flags.get("CPPDEFINES", []), # -D
                       CCFLAGS = flags.get("CCFLAGS", []),
                       CFLAGS = flags.get("CFLAGS", []),
                       CXXFLAGS = flags.get("CXXFLAGS", []),
                       ASFLAGS = flags.get("ASFLAGS", []),
                       LINKFLAGS = flags.get("LINKFLAGS", []),
                       CPPPATH = flags.get("CPPPATH", []), # -I 
                       LIBPATH = flags.get("LIBPATH", []), # -L 
                       LIBS = flags.get("LIBS", []), # -l
                    ) 
    
proj_include = os.path.join(env.subst("$PROJECT_DIR"), "include")
proj_include_km0 = os.path.join(env.subst("$PROJECT_DIR"), "include_km0")
proj_include_km4 = os.path.join(env.subst("$PROJECT_DIR"), "include_km4")

# === Prepare KM0 linker script ===
km0_ld_build = os.path.join(asdk_km0_dir, "build", "rlx8721d.ld")
if not os.path.exists(os.path.dirname(km0_ld_build)):
    os.makedirs(os.path.dirname(km0_ld_build))

# 重新產生 build/rlx8721d.ld
with open(km0_ld_build, "w") as out:
    # append rom_symbol_acut.ld
    rom_sym = os.path.join(asdk_km0_dir, "ld", "rlx8721d_rom_symbol_acut.ld")
    with open(rom_sym, "r") as f:
        out.write(f.read())
        out.write("\n")

    # append img2.ld
    img2_ld = os.path.join(asdk_km0_dir, "ld", "rlx8721d_img2.ld")
    with open(img2_ld, "r") as f:
        out.write(f.read())
        out.write("\n")

print(f">>> Generated merged KM0 ld: {km0_ld_build}")

# === Prepare KM4 linker script ===
km4_ld_build = os.path.join(asdk_km4_dir, "build", "rlx8721d.ld")
if not os.path.exists(os.path.dirname(km4_ld_build)):
    os.makedirs(os.path.dirname(km4_ld_build))

with open(km4_ld_build, "w") as out:
    # append rom_symbol_acut.ld
    rom_sym = os.path.join(asdk_km4_dir, "ld", "rlx8721d_rom_symbol_acut.ld")
    with open(rom_sym, "r") as f:
        out.write(f.read())
        out.write("\n")

    if USE_TZ:
        # append img2_ns.ld （非安全）
        img2_ts = os.path.join(asdk_km4_dir, "ld", "rlx8721d_img2_tz.ld")
        with open(img2_ts, "r") as f:
            out.write(f.read())
            out.write("\n")
    else:
        # append img2_ns.ld （非安全）
        img2_ns = os.path.join(asdk_km4_dir, "ld", "rlx8721d_img2_is.ld")
        with open(img2_ns, "r") as f:
            out.write(f.read())
            out.write("\n")

print(f">>> Generated merged KM4 ld: {km4_ld_build}")

# Build KM0
env_km0 = env.Clone()
set_xtools(env_km0)
apply_ini_build_flags(env_km0)
env_km0.Append(CCFLAGS=[
    "-mcpu=cortex-m0", "-mthumb",
    "-Os", "-ffunction-sections", "-fdata-sections",
    "-fno-common", "-fmessage-length=0",
    "-fno-exceptions", "-fomit-frame-pointer",
    "-Wall", "-Wpointer-arith", "-Wno-strict-aliasing",
    "-Wno-unused-function", "-Wno-unused-variable",
    "-Wno-int-conversion"
])
env_km0.Append(CPPPATH=[proj_include])
env_km0.Append(CPPPATH=[proj_include_km0])
env_km0.Append(CCFLAGS=[
    "-U__ARM_FEATURE_CMSE",
    "-DCONFIG_TRUSTZONE=0",
    "-Wno-attributes"
])
env_km0.Append(CPPPATH=km0_inc, CPPDEFINES=env.get("CPPDEFINES", []))
boot_km0_objs = _mk_objs(env_km0, boot_km0_src, os.path.join(env.subst("$BUILD_DIR"), "amebad/boot_km0/obj"))
boot_km0_elf = env_km0.Program(
    target=os.path.join(env.subst("$BUILD_DIR"), "amebad/boot_km0.elf"),
    source=boot_km0_objs,
    LINKFLAGS=[
        "-mcpu=cortex-m0", "-mthumb",
        "-L" + asdk_km0_dir,
        "-T" + os.path.join(asdk_km0_dir, "ld/rlx8721d_boot.ld"),
        "-T" + os.path.join(asdk_km0_dir, "ld/rlx8721d_rom_symbol_acut.ld"),
        "-nostartfiles", "-nostdlib", "-nodefaultlibs",
        "-Wl,--gc-sections", "-Wl,--warn-section-align",
        "-Wl,-Map=" + os.path.join(build_dir, "km0_boot.map"),
    ]
)
km0_objs = _mk_objs(env_km0, km0_src, os.path.join(env.subst("$BUILD_DIR"), "amebad/km0/obj"))
km0_proj_src = collect_sources(project_km0_dir)
km0_proj_objs = _mk_objs(env_km0, km0_proj_src, os.path.join(env.subst("$BUILD_DIR"), "amebad/km0/obj"))
km0_elf = env_km0.Program(
    target=os.path.join(env.subst("$BUILD_DIR"), "amebad/km0.elf"),
    source=km0_objs + km0_proj_objs,
    LIBPATH=[os.path.join(asdk_km0_dir, "lib/application")],
    LIBS=extra_libs_km0,
    LINKFLAGS=[
        "-mcpu=cortex-m0", "-mthumb",
        "-L" + asdk_km0_dir,
        "-T" + km0_ld_build,
        "-nostartfiles", "--specs=nosys.specs",
        "-Wl,--gc-sections", "-Wl,--warn-section-align",
        "-Wl,-Map=" + os.path.join(build_dir, "target_km0_img2.map"),
        "-Wl,--cref", "-Wl,--no-enum-size-warning",
    ]
)

# Build KM4
env_km4 = env.Clone()
set_xtools(env_km4)
apply_ini_build_flags(env_km4)
env_km4.Append(CCFLAGS=[
    "-mcpu=cortex-m33", "-mthumb", "-mcmse", "-mfpu=fpv5-sp-d16", "-mfloat-abi=hard",
    "-Os", "-ffunction-sections", "-fdata-sections",
    "-fno-common", "-fmessage-length=0",
    "-fno-exceptions", "-fomit-frame-pointer",
    "-Wall", "-Wpointer-arith", "-Wno-strict-aliasing",
    "-Wno-unused-function", "-Wno-unused-variable",
    "-Wno-int-conversion", "-Wno-implicit-function-declaration",
    "-Wno-incompatible-pointer-types"
])
compat_header = os.path.join(proj_include_km4, "compat_sys_types.h").replace("\\","/")
env_km4.Append(CCFLAGS=["-include", compat_header])
env_km4.Append(CCFLAGS=[f"-DosThreadId_t=TaskHandle_t"])
env_km4.Append(CPPPATH=[proj_include])
env_km4.Append(CPPPATH=[proj_include_km4])
env_km4.Append(CPPPATH=km4_inc, CPPDEFINES=env.get("CPPDEFINES", []))
boot_km4_objs = _mk_objs(env_km4, boot_km4_src, os.path.join(env.subst("$BUILD_DIR"), "amebad/boot_km4/obj"))
boot_km4_elf = env_km4.Program(
    target=os.path.join(env.subst("$BUILD_DIR"), "amebad/boot_km4.elf"),
    source=boot_km4_objs,
    LINKFLAGS=[
        "-mcpu=cortex-m33", "-mthumb", "-mcmse", "-mfpu=fpv5-sp-d16", "-mfloat-abi=hard",
        "-L" + asdk_km4_dir,
        "-T" + os.path.join(asdk_km4_dir, "ld/secureboot/rlx8721d_img1_s_sboot.ld"),
        "-T" + os.path.join(asdk_km4_dir, "ld/rlx8721d_rom_symbol_acut_boot.ld"),
        "-nostartfiles", "-nostdlib", "-nodefaultlibs",
        "-Wl,--gc-sections", "-Wl,--warn-section-align",
        "-Wl,-Map=" + os.path.join(build_dir, "km4_boot.map"),
    ]
)
km4_objs = _mk_objs(env_km4, km4_src, os.path.join(env.subst("$BUILD_DIR"), "amebad/km4/obj"))
km4_proj_src = collect_sources(project_km4_dir)
km4_proj_objs = _mk_objs(env_km4, km4_proj_src, os.path.join(env.subst("$BUILD_DIR"), "amebad/km4/obj"))
km4_ns_elf = env_km4.Program(
    target=os.path.join(env.subst("$BUILD_DIR"), "amebad/km4.elf"),
    source=km4_objs + km4_proj_objs,
    LIBPATH=[os.path.join(asdk_km4_dir, "lib/application")],
    LIBS=extra_libs_km4,
    LINKFLAGS=[
        "-mcpu=cortex-m33", "-mthumb", "-mcmse", "-mfpu=fpv5-sp-d16", "-mfloat-abi=hard",
        "-L" + asdk_km4_dir,
        "-T" + km4_ld_build,
        "-nostartfiles", "--specs=nosys.specs",
        "-Wl,--gc-sections", "-Wl,--warn-section-align",
        "-Wl,-Map=" + os.path.join(build_dir, "target_km4_img2.map"),
        "-Wl,--cref", "-Wl,--no-enum-size-warning",
    ]
)

def _run(cmd, strict=True):
    import subprocess, shlex
    # 支援 list 或字串
    if isinstance(cmd, str):
        printable = cmd
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    else:
        printable = " ".join(cmd)
        r = subprocess.run(cmd, capture_output=True, text=True)
    print(">>>", printable)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr)
    if strict and r.returncode != 0:
        raise RuntimeError(f"Command failed: {printable}")
    return r.returncode

def _find_symbol_addr_from_map(map_path: str, *symbols, fallback_elf: str | None = None, fallback_sections: list[str] | None = None) -> int:
    import re, subprocess, os
    # --- 先從 map 尋找（原本兩種嚴格樣式）---
    with open(map_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for sym in symbols:
        pat = re.compile(rf"^\s*{re.escape(sym)}\s*=\s*0x([0-9A-Fa-f]+)\s*$")
        for ln in lines:
            m = pat.match(ln)
            if m:
                return int(m.group(1), 16)

    for sym in symbols:
        pat = re.compile(rf"^\s*0x([0-9A-Fa-f]+)\s+{re.escape(sym)}\s*$")
        for ln in lines:
            m = pat.match(ln)
            if m:
                return int(m.group(1), 16)

    # --- 放寬的 map 掃描（同一行有其他欄位也接受）---
    for sym in symbols:
        pat = re.compile(rf"0x([0-9A-Fa-f]+)\s+.*\b{re.escape(sym)}\b")
        for ln in lines:
            m = pat.search(ln)
            if m:
                return int(m.group(1), 16)

    # --- 從 ELF 的 section 表抓 VMA 當載入位址 ---
    if fallback_elf and fallback_sections:
        try:
            r = subprocess.run([objdump, "-h", fallback_elf], capture_output=True, text=True)
            out = r.stdout
            # objdump -h 的格式大致是：
            # [Nr] Name              Size      VMA       LMA       File off  Algn
            #  12 .ram_image2.text   0000....  20200000  20200000  0000....  2**...
            for sec in fallback_sections:
                pat = re.compile(rf"^\s*\d+\s+{re.escape(sec)}\s+[0-9A-Fa-f]+\s+([0-9A-Fa-f]+)\s+", re.M)
                m = pat.search(out)
                if m:
                    return int(m.group(1), 16)
        except Exception:
            pass

    # --- 最後用 nm 直接找符號 ---
    if fallback_elf and symbols:
        try:
            r = subprocess.run([nm, "-n", fallback_elf], capture_output=True, text=True)
            for ln in r.stdout.splitlines():
                parts = ln.strip().split()
                if len(parts) >= 3:
                    addr_hex, _, name = parts[0], parts[1], parts[2]
                    if name in symbols:
                        return int(addr_hex, 16)
        except Exception:
            pass

    raise RuntimeError(f"symbol {symbols} not found in {map_path}")

def _prepend_header(in_bin: str, map_path: str, symbols, out_bin: str | None = None):
    """
    boot 類影像：雙 magic (BE)
    image2 類影像：ASCII "81958711" + size(LE) + load_addr(LE) + 16B 0xFF
    失敗時會自動回退用 ELF section 取得位址。
    """
    import os, struct, shutil
    from collections.abc import Sequence

    # ---- 常量 ----
    PATTERN_1 = 0x96969999
    PATTERN_2 = 0xFC66CC3F
    IMG2SIGN  = b"81958711"
    RSVD16    = b"\xFF" * 16

    # ---- 正規化輸入 ----
    if isinstance(symbols, (str, bytes)):
        sym_list = [symbols.decode() if isinstance(symbols, bytes) else symbols]
    elif isinstance(symbols, Sequence):
        sym_list = list(symbols)
    else:
        raise TypeError("symbols must be str or sequence of str")

    if out_bin is None:
        root, ext = os.path.splitext(in_bin)
        out_bin = f"{root}_prepend{ext}"

    # ---- 根據 map 名稱猜對應的純淨 ELF （用於 fallback）----
    base_map = os.path.basename(map_path)
    img_dir  = os.path.dirname(map_path)
    guess_elf = None
    if   base_map == "km0_boot.map":          guess_elf = os.path.join(img_dir, "target_pure_loader.axf")
    elif base_map == "km4_boot.map":          guess_elf = os.path.join(img_dir, "target_pure_boot_km4.axf")
    elif base_map == "target_km0_img2.map":   guess_elf = os.path.join(img_dir, "target_km0_pure_img2.axf")
    elif base_map == "target_km4_img2.map":   guess_elf = os.path.join(img_dir, "target_pure_img2.axf")
    elif base_map == "target_img3.map":       guess_elf = os.path.join(img_dir, "target_pure_img3.axf")

    # ---- 根據輸出檔名猜 section 名稱（ELF fallback 用）----
    sec_guess = []
    n = os.path.basename(in_bin)
    if n.endswith("ram_1.bin") or n.endswith("km4_ram_1.bin"):            sec_guess = [".ram_image1.text"]
    elif n.endswith("xip_boot.bin") or n.endswith("km4_xip_boot.bin"):     sec_guess = [".xip_image1.text"]
    elif "ram_2" in n:                                                     sec_guess = [".ram_image2.text"]
    elif "xip_image2" in n:                                                sec_guess = [".xip_image2.text"]
    elif "psram_2" in n:                                                   sec_guess = [".psram_image2.text"]
    elif n.startswith("ram_3_s"):                                          sec_guess = [".ram_image3.text"]
    elif n.startswith("ram_3_nsc"):                                        sec_guess = [".gnu.sgstubs"]
    elif n.startswith("psram_3_s"):                                        sec_guess = [".psram_image3.text"]

    # ---- 真正取位址（先 map 符號 → 再 ELF/section）----
    addr = _find_symbol_addr_from_map(
        map_path, *sym_list,
        fallback_elf=guess_elf,
        fallback_sections=sec_guess
    )

    size = os.path.getsize(in_bin)
    name = os.path.basename(in_bin)

    # boot 影像要雙 magic
    is_boot = name.endswith("ram_1.bin") or name.endswith("xip_boot.bin")
    magic = (struct.pack(">L", PATTERN_1) + struct.pack(">L", PATTERN_2)) if is_boot else IMG2SIGN
    header = magic + struct.pack("<L", size) + struct.pack("<L", addr) + RSVD16

    with open(out_bin, "wb") as w, open(in_bin, "rb") as r:
        w.write(header)
        shutil.copyfileobj(r, w)


def _pad_to_4k(path: str):
    import os
    sz = os.stat(path).st_size
    newsize = (((sz - 1) >> 12) + 1) << 12 if sz else 0
    pad = newsize - sz
    if pad > 0:
        with open(path, "ab", buffering=0) as f:
            for _ in range(pad):
                f.write(b"\xFF")

def _concat_bins(out_path:str, *parts:str):
    with open(out_path, "wb") as w:
        for p in parts:
            if not p: 
                continue
            with open(p, "rb") as r:
                w.write(r.read())

def _load_security_cfg(imgdir):
    """
    來源優先序：
    1) 環境變數（RSIP_ENABLE, RSIP_KEY, RSIP_IV, SBOOT_ENABLE, SBOOT_SEED, RDP_ENABLE, RDP_KEY, SIMG2_ENABLE）
    2) security_config.sh（可能在 sdk/security_config.sh，或以 imagetool.sh 的相對路徑回推）
    """
    cfg = {
        "RSIP_ENABLE": "0", "SBOOT_ENABLE": "0", "RDP_ENABLE": "0", "SIMG2_ENABLE": "0",
        "RSIP_KEY": "", "RSIP_IV": "", "SBOOT_SEED": "", "RDP_KEY": ""
    }
    # 先吃環境變數
    for k in list(cfg.keys()):
        if k in os.environ:
            cfg[k] = os.environ[k]

    # 再找 security_config.sh
    candidates = [
        os.path.join(sdk_dir, "security_config.sh"),
        os.path.normpath(os.path.join(imgdir, "../../../../security_config.sh")),
    ]
    for f in candidates:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    m = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*("?)([^"#]+)\2', line)
                    if m and m.group(1) in cfg:
                        cfg[m.group(1)] = m.group(3).strip()
            break

    # 正規化開關
    def _b(x): return "1" if str(x).strip().lower() in ("1", "true", "y", "yes") else "0"
    for k in ("RSIP_ENABLE","SBOOT_ENABLE","RDP_ENABLE","SIMG2_ENABLE"):
        cfg[k] = _b(cfg[k])
    return cfg

# === KM0 boot 後處理（等同 Makefile linker_loader 段）===
def postprocess_km0_boot():
    print(">>> Post-processing KM0 boot ...")
    elf      = os.path.join(build_dir, "boot_km0.elf")
    if not os.path.exists(elf):
        raise FileNotFoundError("boot_km0.elf not found")

    image_out = build_dir
    map_path  = os.path.join(image_out, "km0_boot.map")
    pure_axf  = os.path.join(image_out, "target_pure_loader.axf")
    ram1_bin  = os.path.join(image_out, "ram_1.bin")
    xip1_bin  = os.path.join(image_out, "xip_boot.bin")

    _run([strip, "-o", pure_axf, elf])
    # 擷取 boot 段
    _run([objcopy, "-j", ".ram_image1.entry", "-j", ".ram_image1.text", "-j", ".ram_image1.data",
          "-Obinary", pure_axf, ram1_bin])
    _run([objcopy, "-j", ".xip_image1.text",
          "-Obinary", pure_axf, xip1_bin])

    # prepend header（符號同原 Makefile）
    ram1_pre = os.path.join(image_out, "ram_1_prepend.bin")
    xip1_pre = os.path.join(image_out, "xip_boot_prepend.bin")
    _prepend_header(ram1_bin, map_path, "__ram_start_table_start__", ram1_pre)
    _prepend_header(xip1_bin, map_path, "__flash_boot_text_start__", xip1_pre)

    # 合併 + 4KB 對齊
    km0_boot_all = os.path.join(image_out, "km0_boot_all.bin")
    _concat_bins(km0_boot_all, xip1_pre, ram1_pre)
    _pad_to_4k(km0_boot_all)

    # 建議：把這段抽成共用 _load_security_cfg(imgdir)（你在 _imagetool_image2_action 裡已寫過一次）
    try:
        imgdir  = os.path.join(asdk_km4_dir, "gnu_utility", "image_tool")
        enctool = os.path.join(imgdir, "EncTool.exe" if os.name == "nt" else "EncTool")
        if os.path.exists(enctool):
            cfg = _load_security_cfg(imgdir)  # 共用的讀取 security_config.sh + env 的函式
            if cfg["RSIP_ENABLE"] == "1":
                img_en = os.path.join(image_out, "km0_boot_all-en.bin")
                _run([enctool, "rsip", km0_boot_all, img_en, "0x08000000", cfg["RSIP_KEY"], cfg["RSIP_IV"]])
                os.replace(img_en, km0_boot_all)
    except Exception as e:
        print(">>> imagetool step (KM0 boot) skipped:", e)

    print(">>> KM0 boot done:", km0_boot_all)
    return km0_boot_all

# === KM0 image2 後處理（等同 Makefile linker_image2 段）===
def postprocess_km0_image2():
    print(">>> Post-processing KM0 image2 ...")
    elf = os.path.join(build_dir, "km0.elf")
    if not os.path.exists(elf):
        raise FileNotFoundError("km0.elf not found")

    image_out = build_dir
    map_path  = os.path.join(image_out, "target_km0_img2.map")
    pure_axf  = os.path.join(image_out, "target_km0_pure_img2.axf")
    ram2_bin  = os.path.join(image_out, "km0_ram_2.bin")
    xip2_bin  = os.path.join(image_out, "km0_xip_image2.bin")
    ret_bin   = os.path.join(image_out, "km0_ram_retention.bin")  # 有就切，沒有就算了

    _run([strip, "-o", pure_axf, elf])
    # 擷取 image2 段
    _run([objcopy, "-j", ".ram_image2.entry", "-j", ".ram_image2.text", "-j", ".ram_image2.data",
          "-Obinary", pure_axf, ram2_bin])
    _run([objcopy, "-j", ".xip_image2.text",
          "-Obinary", pure_axf, xip2_bin])
    # retention 可選
    _run([objcopy, "-j", ".ram_retention.text", "-j", ".ram_retention.entry",
          "-Obinary", pure_axf, ret_bin], strict=False)

    # prepend
    ram2_pre = os.path.join(image_out, "km0_ram_2_prepend.bin")
    xip2_pre = os.path.join(image_out, "km0_xip_image2_prepend.bin")
    _prepend_header(ram2_bin, map_path, "__ram_image2_text_start__", ram2_pre)
    _prepend_header(xip2_bin, map_path, "__flash_text_start__",      xip2_pre)
    if os.path.exists(ret_bin) and os.path.getsize(ret_bin) > 0:
        ret_pre = os.path.join(image_out, "km0_ram_retention_prepend.bin")
        _prepend_header(ret_bin, map_path, "__retention_entry_func__", ret_pre)

    # 合併（依原廠 km0 只併 xip+ram；retention 獨立）
    km0_all = os.path.join(image_out, "km0_image2_all.bin")
    _concat_bins(km0_all, xip2_pre, ram2_pre)
    _pad_to_4k(km0_all)

    print(">>> KM0 image2 done:", km0_all)
    return km0_all

def postprocess_km4_boot():
    """
    依照 Realtek 的 linker_loader 流程，從 boot_km4.elf 萃出
    .ram_image1.{entry,text,data} 與 .xip_image1.text，前置 header 後合併成 km4_boot_all.bin
    並視情況呼叫 imagetool.sh（Makefile 同樣有做）。
    """
    print(">>> Post-processing KM4 boot ...")

    elf = os.path.join(build_dir, "boot_km4.elf")
    if not os.path.exists(elf):
        raise FileNotFoundError("boot_km4.elf not found")

    image_out = build_dir
    map_path  = os.path.join(image_out, "km4_boot.map")
    pure_axf  = os.path.join(image_out, "target_pure_boot_km4.axf")

    ram1_bin  = os.path.join(image_out, "km4_ram_1.bin")
    xip1_bin  = os.path.join(image_out, "km4_xip_boot.bin")

    # strip -> 產出純淨 axf
    _run([strip, "-o", pure_axf, elf])

    # 擷取 boot 段：RAM image1 與 XIP image1（和 Makefile 相同 section）
    _run([objcopy,
          "-j", ".ram_image1.entry", "-j", ".ram_image1.text", "-j", ".ram_image1.data",
          "-Obinary", pure_axf, ram1_bin])

    # XIP 有些配置可能不存在，失敗不致命
    _run([objcopy,
          "-j", ".xip_image1.text",
          "-Obinary", pure_axf, xip1_bin], strict=False)

    # 依 map 取符號地址，前置 header（容忍兩種命名）
    ram1_pre = os.path.join(image_out, "km4_ram_1_prepend.bin")
    xip1_pre = os.path.join(image_out, "km4_xip_boot_prepend.bin")

    _prepend_header(ram1_bin, map_path,
                    ["__ram_start_table_start__", "ram_start_table_start__"],
                    ram1_pre)

    # xip1_bin 可能不存在或為空；存在才前置/合併
    xip_exists = os.path.exists(xip1_bin) and os.path.getsize(xip1_bin) > 0
    if xip_exists:
        _prepend_header(xip1_bin, map_path,
                        ["__flash_boot_text_start__", "flash_boot_text_start__"],
                        xip1_pre)

    # 合併順序：XIP -> RAM（Makefile 如此）
    km4_boot_all = os.path.join(image_out, "km4_boot_all.bin")
    if xip_exists:
        _concat_bins(km4_boot_all, xip1_pre, ram1_pre)
    else:
        _concat_bins(km4_boot_all, ram1_pre)

    # 4KB 對齊（與工具鏈 pad.sh 行為一致）
    _pad_to_4k(km4_boot_all)

    # 套用 sboot/rsip 到 km4_boot_all.bin（純 Python）
    try:
        imgdir  = os.path.join(asdk_km4_dir, "gnu_utility", "image_tool")
        enctool = os.path.join(imgdir, "EncTool.exe" if os.name == "nt" else "EncTool")
        if os.path.exists(enctool):
            # 讀 security_config.sh + 允許環境變數覆蓋
            cfg = {"SBOOT_ENABLE":"0","RSIP_ENABLE":"0","SBOOT_SEED":"", "RSIP_KEY":"","RSIP_IV":""}
            sc = os.path.normpath(os.path.join(imgdir, "../../../../security_config.sh"))
            if os.path.exists(sc):
                with open(sc, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        m = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*("?)([^"#]+)\2', line)
                        if m and m.group(1) in cfg:
                            cfg[m.group(1)] = m.group(3).strip()
            for k in cfg:  # env override
                if k in os.environ:
                    cfg[k] = os.environ[k]
            def _b(x): return "1" if str(x).strip().lower() in ("1","true","y","yes") else "0"
            cfg["SBOOT_ENABLE"] = _b(cfg["SBOOT_ENABLE"])
            cfg["RSIP_ENABLE"]  = _b(cfg["RSIP_ENABLE"])

            img_sb = os.path.join(image_out, "km4_boot_all-sb.bin")
            img_en = os.path.join(image_out, "km4_boot_all-en.bin")
            if cfg["SBOOT_ENABLE"] == "1":
                _run([enctool, "sboot", km4_boot_all, img_sb, os.path.join(imgdir,"key_pair.txt"), cfg["SBOOT_SEED"], "1"])
                os.replace(img_sb, km4_boot_all)
            if cfg["RSIP_ENABLE"] == "1":
                _run([enctool, "rsip",  km4_boot_all, img_en, "0x08004000", cfg["RSIP_KEY"], cfg["RSIP_IV"]])
                os.replace(img_en, km4_boot_all)
    except Exception as e:
        print(">>> imagetool step (boot) skipped:", e)

    print(">>> KM4 boot done:", km4_boot_all)
    return km4_boot_all

# === KM4 image2 後處理 ===
def postprocess_km4_image2_ns():
    print(">>> Post-processing KM4 image2_ns ...")

    elf = os.path.join(build_dir, "km4.elf")
    if not os.path.exists(elf):
        raise FileNotFoundError("km4.elf not found")

    image_out = build_dir
    # 原本寫 target_img2.map → 改成 target_km4_img2.map
    map_path  = os.path.join(image_out, "target_km4_img2.map")
    pure_axf  = os.path.join(image_out, "target_pure_img2.axf")

    ram2_bin  = os.path.join(image_out, "ram_2.bin")
    xip2_bin  = os.path.join(image_out, "xip_image2.bin")
    psram_bin = os.path.join(image_out, "psram_2.bin")

    _run([strip, "-o", pure_axf, elf])

    # 擷取三段（和 Makefile 一致）
    _run([objcopy, "-j", ".ram_image2.entry", "-j", ".ram_image2.text", "-j", ".ram_image2.data",
          "-Obinary", pure_axf, ram2_bin])
    _run([objcopy, "-j", ".xip_image2.text",
          "-Obinary", pure_axf, xip2_bin], strict=False)
    _run([objcopy, "-j", ".psram_image2.text", "-j", ".psram_image2.data",
          "-Obinary", pure_axf, psram_bin], strict=False)  # 有些配置可能沒有 PSRAM

    # prepend（容忍不同符號命名）
    ram2_pre  = os.path.join(image_out, "ram_2_prepend.bin")
    xip2_pre  = os.path.join(image_out, "xip_image2_prepend.bin")
    psram_pre = os.path.join(image_out, "psram_2_prepend.bin")

    _prepend_header(ram2_bin,  map_path, ["__ram_image2_text_start__", "ram_image2_text_start__"],  ram2_pre)
     # 只有在 XIP 檔案真的存在且非空時才前置 header/併入
    xip_exists = os.path.exists(xip2_bin) and os.path.getsize(xip2_bin) > 0
    if xip_exists:
        _prepend_header(xip2_bin,  map_path, ["__flash_text_start__", "flash_text_start__"], xip2_pre)
    else:
        xip2_pre = None

    if os.path.exists(psram_bin):
        _prepend_header(psram_bin, map_path, ["__psram_image2_text_start__", "psram_image2_text_start__"], psram_pre)
    else:
        psram_pre = None

    # 合併順序：xip → ram → psram（Makefile 如此）
    km4_all = os.path.join(image_out, "km4_image2_all.bin")
    _concat_bins(km4_all, xip2_pre, ram2_pre, psram_pre)
    _pad_to_4k(km4_all)

    print(">>> KM4 image2_ns done:", km4_all)
    return km4_all

# ---- 只在 TZ 啟用時做（你可加條件）----
def postprocess_km4_image3_s():
    print(">>> Post-processing KM4 image3 (secure) ...")

    elf = os.path.join(build_dir, "km4_img3.elf")   # 如果你把 image3 也編成不同 elf；否則照 km4.elf
    if not os.path.exists(elf):
        print("skip image3: no elf")
        return None

    image_out = build_dir
    map_path  = os.path.join(image_out, "target_img3.map")
    pure_axf  = os.path.join(image_out, "target_pure_img3.axf")

    ram3s_bin  = os.path.join(image_out, "ram_3_s.bin")
    ram3nsc_bin= os.path.join(image_out, "ram_3_nsc.bin")
    psram3s_bin= os.path.join(image_out, "psram_3_s.bin")

    _run([strip, "-o", pure_axf, elf])
    _run([objcopy, "-j", ".ram_image3.text", "-j", ".ram_image3.data",
          "-Obinary", pure_axf, ram3s_bin])
    _run([objcopy, "-j", ".gnu.sgstubs",
          "-Obinary", pure_axf, ram3nsc_bin])
    _run([objcopy, "-j", ".psram_image3.text", "-j", ".psram_image3.data",
          "-Obinary", pure_axf, psram3s_bin], strict=False)

    ram3s_pre   = os.path.join(image_out, "ram_3_s_prepend.bin")
    ram3nsc_pre = os.path.join(image_out, "ram_3_nsc_prepend.bin")
    psram3s_pre = os.path.join(image_out, "psram_3_s_prepend.bin")

    _prepend_header(ram3s_bin,   map_path, ["__ram_image3_text_start__", "ram_image3_text_start__"],   ram3s_pre)
    _prepend_header(ram3nsc_bin, map_path, ["__ram_image3_nsc_start__",  "ram_image3_nsc_start__"],    ram3nsc_pre)
    if os.path.exists(psram3s_bin):
        _prepend_header(psram3s_bin, map_path, ["__psram_image3_text_start__", "psram_image3_text_start__"], psram3s_pre)
    else:
        psram3s_pre = None

    km4_img3_all   = os.path.join(image_out, "km4_image3_all.bin")
    km4_img3_psram = os.path.join(image_out, "km4_image3_psram.bin")

    _concat_bins(km4_img3_all, ram3s_pre, ram3nsc_pre)
    _pad_to_4k(km4_img3_all)

    if psram3s_pre:
        _concat_bins(km4_img3_psram, psram3s_pre)
        _pad_to_4k(km4_img3_psram)

    print(">>> KM4 image3 done:", km4_img3_all, "(psram:", bool(psram3s_pre), ")")
    return km4_img3_all

# === 綁定到 SCons target（用 ELF 當輸入觸發） ===
def _post_km0_boot_action(target, source, env):
    postprocess_km0_boot()
    return 0

def _post_km4_boot_action(target, source, env):
    postprocess_km4_boot()
    return 0

def _post_km0_action(target, source, env):
    postprocess_km0_image2()
    return 0

def _post_km4_image2_ns_action(target, source, env):
    postprocess_km4_image2_ns()
    return 0

km0_boot_bin = env.Command(os.path.join(build_dir, "km0_boot_all.bin"), boot_km0_elf, _post_km0_boot_action)
km0_all_bin  = env.Command(os.path.join(build_dir, "km0_image2_all.bin"), km0_elf,  _post_km0_action)

km4_boot_bin = env.Command(os.path.join(build_dir, "km4_boot_all.bin"), boot_km4_elf, _post_km4_boot_action)
km4_all_bin = env.Command(os.path.join(build_dir, "km4_image2_all.bin"), km4_ns_elf, _post_km4_image2_ns_action)

def _imagetool_image2_action(target, source, env):
    """
    Python 版 imagetool：移植自 sdk 的 gnu_utility/image_tool/imagetool.sh
    - 會根據檔名執行 sboot/rsip/rdp
    - 4KB 對齊
    - 依原腳本順序合併 km0/km4 image2，並視 RDP/BUILD_TYPE 併入 image3
    - 不依賴 bash，支援 Windows / Linux / macOS
    """
    import os, re, shutil, platform

    image_out = build_dir
    km4_all   = os.path.join(image_out, "km4_image2_all.bin")
    km0_all   = os.path.join(image_out, "km0_image2_all.bin")
    copy_path = image_out  # 你目前就放同資料夾
    build_type = os.environ.get("BUILD_TYPE", "NONE")

    # ---- helpers ----
    def _find_imgtool_dir():
        candidates = [
            os.path.join(asdk_km4_dir, "gnu_utility", "image_tool"),
            os.path.join(sdk_dir,       "utility",    "image_tool"),
        ]
        for d in candidates:
            if os.path.isdir(d):
                return d
        raise FileNotFoundError("image_tool folder not found under:\n  " +
                                "\n  ".join(candidates))

    def _enctool_path(imgdir):
        exe = os.path.join(imgdir, "EncTool.exe" if os.name == "nt" else "EncTool")
        if not os.path.exists(exe):
            raise FileNotFoundError("EncTool not found at: " + exe)
        if os.name != "nt":
            try: os.chmod(exe, 0o755)
            except Exception: pass
        return exe

    def _mv(src, dst):
        if os.path.exists(src):
            os.replace(src, dst)

    def _cp(src, dst):
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # 包工具
    imgdir  = _find_imgtool_dir()
    enctool = _enctool_path(imgdir)
    cfg     = _load_security_cfg(imgdir)

    def _rsip(infile, outfile, addr_hex):
        return _run([enctool, "rsip", infile, outfile, addr_hex, cfg["RSIP_KEY"], cfg["RSIP_IV"]])

    def _sboot(infile, outfile, mode):
        keypair = os.path.join(imgdir, "key_pair.txt")
        return _run([enctool, "sboot", infile, outfile, keypair, cfg["SBOOT_SEED"], str(mode)])

    def _rdp(infile, outfile):
        return _run([enctool, "rdp", infile, outfile, cfg["RDP_KEY"]])

    # ---- 依檔名流程（只需要處理 image2；boot/image3 另外呼叫時也能用這一套）----
    def _process_file(image_fullname):
        image_filename = os.path.basename(image_fullname)
        curr_path = os.path.dirname(image_fullname)
        image_name_en = f"{os.path.splitext(image_fullname)[0]}-en{os.path.splitext(image_fullname)[1]}"
        image_name_sb = f"{os.path.splitext(image_fullname)[0]}-sb{os.path.splitext(image_fullname)[1]}"

        # km0/4 boot（供通用性）
        if image_filename == "km0_boot_all.bin" and cfg["RSIP_ENABLE"] == "1":
            _rsip(image_fullname, image_name_en, "0x08000000"); _mv(image_name_en, image_fullname)

        if image_filename == "km4_boot_all.bin":
            if cfg["SBOOT_ENABLE"] == "1":
                _sboot(image_fullname, image_name_sb, 1); _mv(image_name_sb, image_fullname)
            if cfg["RSIP_ENABLE"] == "1":
                _rsip(image_fullname, image_name_en, "0x08004000"); _mv(image_name_en, image_fullname)

        # image3（供通用性；原腳本是產生 -en 檔，原檔不覆蓋）
        if image_filename in ("km4_image3_all.bin", "km4_image3_psram.bin") and cfg["RDP_ENABLE"] == "1":
            _rdp(image_fullname, image_name_en)

        # psram_2_prepend（供通用性）
        if image_filename == "psram_2_prepend.bin" and cfg["SIMG2_ENABLE"] == "1":
            _sboot(image_fullname, image_name_sb, 0); _cp(image_name_sb, image_fullname)

        # === km4_image2_all.bin 主流程 ===
        if image_filename == "km4_image2_all.bin":
            # sboot(2) + pad
            if cfg["SIMG2_ENABLE"] == "1":
                _sboot(image_fullname, image_name_sb, 2); _cp(image_name_sb, image_fullname)
                _pad_to_4k(image_fullname)

            # rsip（會產出 -en）
            km4_for_merge = image_fullname
            if cfg["RSIP_ENABLE"] == "1":
                _rsip(image_fullname, image_name_en, "0x0e000000")
                km4_for_merge = image_name_en

            # 需要 km0 才能合併
            if not os.path.exists(os.path.join(copy_path, "km0_image2_all.bin")):
                print(">>> km0_image2_all.bin not found; skip merge")
                return 0

            km0_src = os.path.join(copy_path, "km0_image2_all.bin")
            km0_for_merge = km0_src
            if cfg["RSIP_ENABLE"] == "1":
                km0_en = os.path.join(copy_path, "km0_image2_all-en.bin")
                _rsip(km0_src, km0_en, "0x0c000000")
                km0_for_merge = km0_en

            # 合併順序（與腳本一致）：KM0 在前，KM4 在後 → 先 tmp，再視 RDP/image3 決定是否再併
            tmp = os.path.join(curr_path, "km0_km4_image2_tmp.bin")
            final = os.path.join(curr_path, "km0_km4_image2.bin")
            _concat_bins(tmp, km0_for_merge, km4_for_merge)

            # 若 RDP_ENABLE=1 且有 image3 的 -en，依 BUILD_TYPE 併入
            if cfg["RDP_ENABLE"] == "1":
                img3_all_en   = os.path.join(curr_path, "km4_image3_all-en.bin")
                img3_psram_en = os.path.join(curr_path, "km4_image3_psram-en.bin")
                img3_all_raw  = os.path.join(curr_path, "km4_image3_all.bin")
                img3_psram_raw= os.path.join(curr_path, "km4_image3_psram.bin")

                if os.path.exists(img3_all_en):
                    if build_type == "MFG":
                        _concat_bins(final, tmp, img3_all_raw, img3_psram_raw)
                    else:
                        _concat_bins(final, tmp, img3_all_en, img3_psram_en)
                    try: os.remove(tmp)
                    except OSError: pass
                else:
                    _mv(tmp, final)
            else:
                _mv(tmp, final)

            # 複製到 copy_path（與腳本一致）
            _cp(final, os.path.join(copy_path, "km0_km4_image2.bin"))
            return 0

        # === km0_image2_all.bin 對稱流程（腳本也支援）===
        if image_filename == "km0_image2_all.bin":
            km0_for_merge = image_fullname
            if cfg["RSIP_ENABLE"] == "1":
                _rsip(image_fullname, image_name_en, "0x0c000000")
                km0_for_merge = image_name_en

            if not os.path.exists(os.path.join(copy_path, "km4_image2_all.bin")):
                print(">>> km4_image2_all.bin not found; skip merge")
                return 0

            km4_src = os.path.join(copy_path, "km4_image2_all.bin")
            km4_for_merge = km4_src
            if cfg["RSIP_ENABLE"] == "1":
                km4_en = os.path.join(copy_path, "km4_image2_all-en.bin")
                _rsip(km4_src, km4_en, "0x0e000000")
                km4_for_merge = km4_en

            tmp   = os.path.join(curr_path, "km0_km4_image2_tmp.bin")
            final = os.path.join(curr_path, "km0_km4_image2.bin")
            _concat_bins(tmp, km0_for_merge, km4_for_merge)

            if cfg["RDP_ENABLE"] == "1":
                img3_all_en   = os.path.join(copy_path, "km4_image3_all-en.bin")
                img3_psram_en = os.path.join(copy_path, "km4_image3_psram-en.bin")
                if os.path.exists(img3_all_en):
                    _concat_bins(final, tmp, img3_all_en, img3_psram_en)
                    try: os.remove(tmp)
                    except OSError: pass
                else:
                    _mv(tmp, final)
            else:
                _mv(tmp, final)

            _cp(final, os.path.join(copy_path, "km0_km4_image2.bin"))
            return 0

        # 其他檔名：不處理
        return 0

    # 這個 action 會被綁在輸出 km0_km4_image2.bin 上；我們以「km4_image2_all.bin」為主執行一遍，
    # 若不存在就嘗試 km0 分支，否則直接成功返回。
    if os.path.exists(km4_all):
        return _process_file(km4_all)
    elif os.path.exists(km0_all):
        return _process_file(km0_all)
    else:
        print(">>> Neither km4_image2_all.bin nor km0_image2_all.bin exists; nothing to do.")
        return 0

# 用 imagetool 產出最終包（會在 build_dir 生成 km0_km4_image2.bin）
km0_km4_image2_bin = env.Command(
    os.path.join(build_dir, "km0_km4_image2.bin"),
    [km0_all_bin, km4_all_bin],
    _imagetool_image2_action
)
Alias("buildprog", [km0_km4_image2_bin])  # 取代原本的人工 concat 版本

# --- Upload --- 
def upload_amebad(source, target, env): 
    print(">>> Uploading AmebaD image ...")
    # 讀取 platformio.ini 設定 
    port = env.GetProjectOption("upload_port")
    km0 = os.path.join(build_dir, "km0_image2_all.bin")
    km4 = os.path.join(build_dir, "km4_image2_all.bin")
    tool_exe = os.path.join(sdk_dir, "tools", "DownloadServer", "DownloadServer.exe")
    _run(f"\"{tool_exe}\" {port} {km0} {km4}")
    print(">>> Upload done!") 

# 🚩 Upload target (只負責上傳，不會在 build 時觸發)
upload_target = env.Alias("upload", km0_km4_image2_bin, upload_amebad)
AlwaysBuild(upload_target) # 確保 pio run -t upload 會跑