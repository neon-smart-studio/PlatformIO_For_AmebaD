/* include/compat_sys_types.h */
#ifndef COMPAT_SYS_TYPES_H
#define COMPAT_SYS_TYPES_H

#include <stdint.h>

/* 如果系統沒定義 in_addr_t，這裡補一個 */
#ifndef _IN_ADDR_T_DECLARED
typedef uint32_t in_addr_t;
#define _IN_ADDR_T_DECLARED
#endif

#include <sys/time.h>  // 用 toolchain 版本

/* 其他常見缺項（如果還有錯，可在這裡補） */
/* typedef uint32_t in_port_t; */

#endif /* COMPAT_SYS_TYPES_H */
