/**
 * @file lv_types.h
 *
 */

#ifndef LV_TYPES_H
#define LV_TYPES_H

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/
#include <stdint.h>

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**
 * LVGL error codes.
 */
enum {
    LV_RES_INV = 0, /*Typically indicates that the object is deleted (become invalid) in the action
                       function or an operation was failed*/
    LV_RES_OK,      /*The object is valid (no deleted) after the action*/
};

typedef uint8_t lv_res_t;
typedef uintptr_t lv_uintptr_t;

/**********************
 * GLOBAL PROTOTYPES
 **********************/

/**********************
 *      MACROS
 **********************/

#define LV_UNUSED(x) ((void) x)

#define _LV_CONCAT(x, y) x ## y
#define LV_CONCAT(x, y) _LV_CONCAT(x, y)

#define _LV_CONCAT3(x, y, z) x ## y ## z
#define LV_CONCAT3(x, y, z) _LV_CONCAT3(x, y, z)

#if (defined(__clang__) || defined(__GNUC__) || defined(__GNUG__)) && !defined(PYCPARSER)
#define LV_FORMAT_ATTRIBUTE(fmtstr, vararg) __attribute__ ((format(printf, fmtstr, vararg)))
#else
#define LV_FORMAT_ATTRIBUTE(fmtstr, vararg)
#endif

#ifdef __cplusplus
} /*extern "C"*/
#endif

#endif /*LV_TYPES_H*/
