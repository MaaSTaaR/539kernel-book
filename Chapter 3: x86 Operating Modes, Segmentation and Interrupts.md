# x86 Operating Modes, Segmentation and Interrupts

## Introduction

In our situation, and by using modern terminology, we can view the processor as a *library* and *framework*, it provides us with a bunch of instructions to perform whatever we want, also it has general rules that organize the overall environment of execution, that is, it forces us to work in a specific way. We have seen some aspects of the first part when we have written the bootloader, that is, we have seen the processor as a library. In this chapter, we are going to see how the processor works as a framework by examining some important and basic concepts of x86. We need to understand these concepts to start the real work of writing 539kernel.

## x86 Operating Modes

In x86 an operating mode specifies the overall picture of the processor, such as how does it perform its tasks, the maximum size of available registers, the available advanced features for the running operating system and the restrictions.

When we developed the bootloader in the previous chapter we have worked with *x86 operating mode* named *real mode* ^[Its full name is *real address mode*.] which is an old operating mode which is still supported by modern x86 processors for the sake of backward compatibility and when the computer runs initially, it runs on real mode, for the same reason of backward compatibility.


Real mode is a 16-bit operating mode which means that, maximally, only 16-bit of register size can be used, even if the actual size of the registers is 64-bit ^[64-bit CPUs.]. Using only 16-bit of registers has consequences other than the size itself ^[These consequences are considered as disadvantages in modern days.] for example, in real mode the size of the main memory is limited, even if the computer has 16GB of memory, real mode can deal with only 1MB. Furthermore, any code which runs on real mode should be 16-bit code, for example, the aforementioned 32-bit registers (such as `eax`) cannot be used in real mode, their 16-bit counterparts should be used instead, for example, the 16-bit `ax` should be used instead of `eax` and so on.

Some core features of modern operating systems nowadays are multitaksing, memory protection and virtual memory ^[If some of these terms are new for you don't worry about them to much, you will learn them gradually through this book.] and real mode provides nothing to to implement these features. However, in modern x86 processors, new and more advanced operating modes have been introduction, namely, they are *protected mode* which is a 32-bit operating mode and *long mode* which is a relatively new 64-bit operating mode. Although the long mode provides more capacity for its users ^[For example, long mode can deal with 16 **exabytes** of memory.] we are going to focus on protected mode since it provides the same basic mechanisms that we need to develop a modern operating system kernel with the aforementioned features, hence, 539kernel is a 32-bit kernel which runs under protected mode.

As we have said, protected mode is a 32-bit operating mode, that is, registers with the size of 32-bit can be used, also, protected mode has the ability to deal with 4GB of main memory, and most importantly, it provides important features which we are going to explore through this book that helps us in implementing modern operating system kernel features.

## x86 Segmentation

<!--
### Segmentation in Real Mode
### Segmentation in Protected Mode

## x86 Interrupts
-->

<!--
there is a way to switch from Real Mode to Protected Mode, but that's a story for a different day!
-->
