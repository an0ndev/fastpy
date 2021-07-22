#pragma once
#include "base.hpp"
#include "types.hpp"
#include <string>
#include <tuple>
#include <iostream>

namespace libfastpy::functions {
    void _print (Ref <types::String> str) {
        printf ("%s", (*str).value.c_str ());
    }
    template <typename Stringable>
    void _print (Ref <Stringable> str) {
        printf ("%s", (*str).__str__ ().value.c_str ());
    }

    template <typename... Objects>
    void print (std::tuple <Objects...> objects, Ref <types::String> sep, Ref <types::String> end) {
        int objectIndex = 0;
        std::apply ([&objectIndex, &sep] (auto & ...object) {
            (..., [&object, &objectIndex, &sep] () {
                _print (object);

                if (objectIndex < ((std::tuple_size <std::tuple <Objects...>>::value) - 1)) {
                    printf ("%s", (*sep).value.c_str ());
                }
                objectIndex++;
            } ());
        }, objects);
        printf ("%s", (*end).value.c_str ());
    }
};