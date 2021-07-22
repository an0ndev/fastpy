#pragma once

#include <cstdint>
#include <cstdio>

namespace libfastpy {
    template <typename Encapsulated>
    class Ref {
        Encapsulated* inner;
        uintmax_t* referenceCount;
    public:
        template <typename ...EncapsulatedCtorArgs>
        Ref (EncapsulatedCtorArgs ...encapsulatedCtorArgs) : inner (new Encapsulated (encapsulatedCtorArgs...)), referenceCount (new uintmax_t (1)) {};
        Ref (Ref const & old) /* copy-constructor */
        : inner (old.inner), referenceCount (old.referenceCount) {
            (*referenceCount)++;
        }
        Ref (Ref const && old) /* move-constructor */
        : inner (old.inner), referenceCount (old.referenceCount) {
            (*referenceCount)++;
        }
        Encapsulated & operator* () {
            return *inner;
        }
        ~Ref () {
            (*referenceCount)--;
            if ((*referenceCount) == 0) {
                delete referenceCount;
                delete inner;
            }
        }
    };
};