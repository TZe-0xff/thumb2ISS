
# core.CurrentCond()
# =============
core.bits(4) core.CurrentCond();
constant core.bits(2) EL3 = '11';
constant core.bits(2) EL2 = '10';
constant core.bits(2) EL1 = '01';
constant core.bits(2) EL0 = '00';
# core.HaveEL()
# ========
# Return True if Exception level 'el' is supported
boolean core.HaveEL(core.bits(2) el)
    if el IN {EL1,EL0}:
        return True;                             # EL1 and EL0 must exist
    return IMPLEMENTATION_DEFINED = False;
# core.HaveAArch32()
# =============
# Return True if AArch32 state is supported at at least EL0.
boolean core.HaveAArch32()
    return boolean IMPLEMENTATION_DEFINED "AArch32 state is supported at at least EL0";
# core.HaveAArch64()
# =============
# Return True if the highest Exception level is using AArch64 state.
boolean core.HaveAArch64()
    return boolean IMPLEMENTATION_DEFINED "Highest EL using AArch64";
# core.HighestEL()
# ===========
# Returns the highest implemented Exception level.
core.bits(2) core.HighestEL()
    if core.HaveEL(EL3):
        return EL3;
    elsif core.HaveEL(EL2):
        return EL2;
    else:
        return EL1;
# core.HaveAArch32EL()
# ===============
boolean core.HaveAArch32EL(core.bits(2) el)
    # Return True if Exception level 'el' supports AArch32 in this implementation
    if not core.HaveEL(el):
        return False;                    # The Exception level is not implemented
    elsif not core.HaveAArch32():
        return False;                    # No Exception level can use AArch32
    elsif not core.HaveAArch64():
        return True;                     # All Exception levels are using AArch32
    elsif el == core.HighestEL():
        return False;                    # The highest Exception level is using AArch64
    elsif el == EL0:
        return True;                     # EL0 must support using AArch32 if any AArch32
    return IMPLEMENTATION_DEFINED = False;
# core.HaveSecureEL2Ext()
# ==================
# Returns True if Secure EL2 is implemented.
boolean core.HaveSecureEL2Ext()
    return core.IsFeatureImplemented(FEAT_SEL2);
# core.HaveVirtHostExt()
# =================
boolean core.HaveVirtHostExt()
    return core.IsFeatureImplemented(FEAT_VHE);
# ProcState
# =========
# Armv8 processor state bits.
# There is no significance to the field order.
type ProcState is (
    bits (1) N,        # Negative condition flag
    bits (1) Z,        # Zero condition flag
    bits (1) C,        # Carry condition flag
    bits (1) V,        # Overflow condition flag
    bits (1) D,        # Debug mask bit                     [AArch64 only]
    bits (1) A,        # SError interrupt mask bit
    bits (1) I,        # IRQ mask bit
    bits (1) F,        # FIQ mask bit
    bits (1) EXLOCK,   # Lock exception return state
    bits (1) PAN,      # Privileged Access Never Bit        [v8.1]
    bits (1) UAO,      # User Access Override               [v8.2]
    bits (1) DIT,      # Data Independent Timing            [v8.4]
    bits (1) TCO,      # Tag Check Override                 [v8.5, AArch64 only]
    bits (1) PM,       # PMU exception Mask
    bits (1) PPEND,     # synchronous PMU exception to be observed
    bits (2) BTYPE,    # Branch Type                        [v8.5]
    bits (1) ZA,       # Accumulation array enabled         [SME]
    bits (1) SM,       # Streaming SVE mode enabled         [SME]
    bits (1) ALLINT,   # Interrupt mask bit
    bits (1) SS,       # Software step bit
    bits (1) IL,       # Illegal Execution state bit
    bits (2) EL,       # Exception level
    bits (1) nRW,      # Execution state: 0=AArch64, 1=AArch32
    bits (1) SP,       # Stack pointer select: 0=SP0, 1=SPx [AArch64 only]
    bits (1) Q,        # Cumulative saturation flag         [AArch32 only]
    bits (4) GE,       # Greater than or Equal flags        [AArch32 only]
    bits (1) SSBS,     # Speculative Store Bypass Safe
    bits (8) IT,       # If-then bits, RES0 in CPSR         [AArch32 only]
    bits (1) J,        # J bit, RES0                        [AArch32 only, RES0 in SPSR and CPSR]
    bits (1) T,        # T32 bit, RES0 in CPSR              [AArch32 only]
    bits (1) E,        # Endianness bit                     [AArch32 only]
    bits (5) M         # Mode field                         [AArch32 only]
)
ProcState core.APSR;
# core.ELStateUsingAArch32K()
# ======================
(boolean,boolean) core.ELStateUsingAArch32K(core.bits(2) el, boolean secure)
    # Returns (known, aarch32):
    #   'known'   is False for EL0 if the current Exception level is not EL0 and EL1 is
    #             using AArch64, since it cannot determine the state of EL0; True otherwise.
    #   'aarch32' is True if the specified Exception level is using AArch32; False otherwise.
    if not core.HaveAArch32EL(el):
        return (True, False);   # Exception level is using AArch64
    elsif secure and el == EL2:
        return (True, False);   # Secure EL2 is using AArch64
    elsif not core.HaveAArch64():
        return (True, True);    # Highest Exception level, therefore all levels are using AArch32
    # Remainder of function deals with the interprocessing cases when highest
    # Exception level is using AArch64
    boolean aarch32 = UNKNOWN = False;
    boolean known = True;
    aarch32_below_el3 = (core.HaveEL(EL3) and (not secure or not core.HaveSecureEL2Ext() or SCR_EL3.EEL2 == '0') and
                         SCR_EL3.RW == '0');
    aarch32_at_el1 = (aarch32_below_el3 or
                      (core.HaveEL(EL2) and (not secure or (core.HaveSecureEL2Ext() and SCR_EL3.EEL2 == '1')) and
                       not (core.HaveVirtHostExt() and HCR_EL2.<E2H,TGE> == '11') and
                       HCR_EL2.RW == '0'));
    if el == EL0 and not aarch32_at_el1:
               # Only know if EL0 using AArch32 from core.APSR
        if core.APSR.EL == EL0:
            aarch32 = core.APSR.nRW == '1';       # EL0 controlled by core.APSR
        else:
            known = False;                     # EL0 state is UNKNOWN
    else:
        aarch32 = (aarch32_below_el3 and el != EL3) or (aarch32_at_el1 and el IN {EL1,EL0});
    if not known:
         aarch32 = UNKNOWN = False;
    return (known, aarch32);
# core.ELStateUsingAArch32()
# =====================
boolean core.ELStateUsingAArch32(core.bits(2) el, boolean secure)
    # See core.ELStateUsingAArch32K() for description. Must only be called in circumstances where
    # result is valid (typically, that means 'el IN {EL1,EL2,EL3}').
    (known, aarch32) = core.ELStateUsingAArch32K(el, secure);
    assert known;
    return aarch32;
type SCRType;
# core.Replicate()
# ===========
core.bits(M*N) core.Replicate(core.bits(M) x, integer N);
# core.Zeros()
# =======
core.bits(N) core.Zeros(integer N)
    return core.Replicate('0',N);
# core.ZeroExtend()
# ============
core.bits(N) core.ZeroExtend(core.bits(M) x, integer N)
    assert N >= M;
    return core.Zeros(N-M) : x;
# SCR_GEN[]
# =========
SCRType SCR_GEN[]
    # AArch32 secure & AArch64 EL3 registers are not architecturally mapped
    assert core.HaveEL(EL3);
    r = 0;
    if not core.HaveAArch64():
        r = core.ZeroExtend(SCR, 64);
    else:
        r = SCR_EL3;
    return r;
# core.IsSecureBelowEL3()
# ==================
# Return True if an Exception level below EL3 is in Secure state
# or would be following an exception return to that level.
#
# Differs from IsSecure in that it ignores the current EL or Mode
# in considering security state.
# That is, if at AArch64 EL3 or in AArch32 Monitor mode, whether an
# exception return would pass to Secure or Non-secure state.
boolean core.IsSecureBelowEL3()
    if core.HaveEL(EL3):
        return SCR_GEN[].NS == '0';
    elsif core.HaveEL(EL2) and (not core.HaveSecureEL2Ext() or not core.HaveAArch64()):
        # If Secure EL2 is not an architecture option then we must be Non-secure.
        return False;
    else:
        # True if processor is Secure or False if Non-secure.
        return boolean IMPLEMENTATION_DEFINED "Secure-only implementation";
# core.ELUsingAArch32()
# ================
boolean core.ELUsingAArch32(core.bits(2) el)
    return core.ELStateUsingAArch32(el, core.IsSecureBelowEL3());
# core.SecureOnlyImplementation()
# ==========================
# Returns True if the security state is always Secure for this implementation.
boolean core.SecureOnlyImplementation()
    return boolean IMPLEMENTATION_DEFINED "Secure-only implementation";
# core.IsSecureEL2Enabled()
# ====================
# Returns True if Secure EL2 is enabled, False otherwise.
boolean core.IsSecureEL2Enabled()
    if core.HaveEL(EL2) and core.HaveSecureEL2Ext():
        if core.HaveEL(EL3):
            if not core.ELUsingAArch32(EL3) and SCR_EL3.EEL2 == '1':
                return True;
            else:
                return False;
        else:
            return core.SecureOnlyImplementation();
    else:
        return False;
# core.EL2Enabled()
# ============
# Returns True if EL2 is present and executing
# - with the PE in Non-secure state when Non-secure EL2 is implemented, or
# - with the PE in Realm state when Realm EL2 is implemented, or
# - with the PE in Secure state when Secure EL2 is implemented and enabled, or
# - when EL3 is not implemented.
boolean core.EL2Enabled()
    return core.HaveEL(EL2) and (not core.HaveEL(EL3) or SCR_GEN[].NS == '1' or core.IsSecureEL2Enabled());
# core.GeneralExceptionsToAArch64()
# ====================================
# Returns True if exceptions normally routed to EL1 are being handled at an Exception
# level using AArch64, because either EL1 is using AArch64 or TGE is in force and EL2
# is using AArch64.
boolean core.GeneralExceptionsToAArch64()
    return ((core.APSR.EL == EL0 and not core.ELUsingAArch32(EL1)) or
            (core.EL2Enabled() and not core.ELUsingAArch32(EL2) and HCR_EL2.TGE == '1'));
# Exception
# =========
# Classes of exception.
enumeration Exception {
        Exception_Uncategorized,        # Uncategorized or unknown reason
        Exception_WFxTrap,              # Trapped WFI or WFE instruction
        Exception_CP15RTTrap,           # Trapped AArch32 MCR or MRC access, coproc=0b111
        Exception_CP15RRTTrap,          # Trapped AArch32 MCRR or MRRC access, coproc=0b1111
        Exception_CP14RTTrap,           # Trapped AArch32 MCR or MRC access, coproc=0b1110
        Exception_CP14DTTrap,           # Trapped AArch32 LDC or STC access, coproc=0b1110
        Exception_CP14RRTTrap,          # Trapped AArch32 MRRC access, coproc=0b1110
        Exception_AdvSIMDFPAccessTrap,  # HCPTR-trapped access to SIMD or FP
        Exception_FPIDTrap,             # Trapped access to SIMD or FP ID register
        Exception_LDST64BTrap,          # Trapped access to ST64BV, ST64BV0, ST64B and LD64B
        # Trapped BXJ instruction not supported in Armv8
        Exception_PACTrap,               # Trapped invalid PAC use
        Exception_IllegalState,          # Illegal Execution state
        Exception_SupervisorCall,        # Supervisor Call
        Exception_HypervisorCall,        # Hypervisor Call
        Exception_MonitorCall,           # Monitor Call or Trapped SMC instruction
        Exception_SystemRegisterTrap,    # Trapped MRS or MSR System register access
        Exception_ERetTrap,              # Trapped invalid ERET use
        Exception_InstructionAbort,      # Instruction Abort or Prefetch Abort
        Exception_PCAlignment,           # PC alignment fault
        Exception_DataAbort,             # Data Abort
        Exception_NV2DataAbort,          # Data abort at EL1 reported as being from EL2
        Exception_PACFail,               # PAC Authentication failure
        Exception_SPAlignment,           # SP alignment fault
        Exception_FPTrappedException,    # IEEE trapped FP exception
        Exception_SError,                # SError interrupt
        Exception_Breakpoint,            # (Hardware) Breakpoint
        Exception_SoftwareStep,          # Software Step
        Exception_Watchpoint,            # Watchpoint
        Exception_NV2Watchpoint,         # Watchpoint at EL1 reported as being from EL2
        Exception_SoftwareBreakpoint,    # Software Breakpoint Instruction
        Exception_VectorCatch,           # AArch32 Vector Catch
        Exception_IRQ,                   # IRQ interrupt
        Exception_SVEAccessTrap,         # HCPTR trapped access to SVE
        Exception_SMEAccessTrap,         # HCPTR trapped access to SME
        Exception_TSTARTAccessTrap,      # Trapped TSTART access
        Exception_GPC,                   # Granule protection check
        Exception_BranchTarget,          # Branch Target Identification
        Exception_MemCpyMemSet,          # Exception from a CPY* or SET* instruction
        Exception_GCSFail,               # GCS Exceptions
        Exception_SystemRegister128Trap, # Trapped MRRS or MSRR System register or SYSP access
        Exception_FIQ};                 # FIQ interrupt
# core.ThisInstrLength()
# =================
integer core.ThisInstrLength();
# core.Unreachable()
# =============
core.Unreachable()
    assert False;
# core.ExceptionClass()
# ========================
# Returns the Exception Class and Instruction Length fields to be reported in HSR
(integer,bit) core.ExceptionClass(Exception exceptype)
    il_is_valid = True;
    ec = 0;
    case exceptype of
        when Exception_Uncategorized         ec = 0x00; il_is_valid = False;
        when Exception_WFxTrap               ec = 0x01;
        when Exception_CP15RTTrap            ec = 0x03;
        when Exception_CP15RRTTrap           ec = 0x04;
        when Exception_CP14RTTrap            ec = 0x05;
        when Exception_CP14DTTrap            ec = 0x06;
        when Exception_AdvSIMDFPAccessTrap   ec = 0x07;
        when Exception_FPIDTrap              ec = 0x08;
        when Exception_PACTrap               ec = 0x09;
        when Exception_TSTARTAccessTrap      ec = 0x1B;
        when Exception_GPC                   ec = 0x1E;
        when Exception_CP14RRTTrap           ec = 0x0C;
        when Exception_BranchTarget          ec = 0x0D;
        when Exception_IllegalState          ec = 0x0E; il_is_valid = False;
        when Exception_SupervisorCall        ec = 0x11;
        when Exception_HypervisorCall        ec = 0x12;
        when Exception_MonitorCall           ec = 0x13;
        when Exception_InstructionAbort      ec = 0x20; il_is_valid = False;
        when Exception_PCAlignment           ec = 0x22; il_is_valid = False;
        when Exception_DataAbort             ec = 0x24;
        when Exception_NV2DataAbort          ec = 0x25;
        when Exception_FPTrappedException    ec = 0x28;
        otherwise                            core.Unreachable();
    if ec IN {0x20,0x24} and core.APSR.EL == EL2:
        ec = ec + 1;
    bit il;
    if il_is_valid:
        il = '1' if core.ThisInstrLength() == 32 else '0';
    else:
        il = '1';
    return (ec,il);
# PASpace
# =======
# Physical address spaces
enumeration PASpace {
    PAS_NonSecure,
    PAS_Secure,
    PAS_Root,
    PAS_Realm
};
# FullAddress
# ===========
# Physical or Intermediate Physical Address type1.
# Although AArch32 only has access to 40 bits of physical or intermediate physical address space,
# the full address type1 has 56 bits to allow interprocessing with AArch64.
# The maximum physical or intermediate physical address size is IMPLEMENTATION DEFINED,
# but never exceeds 56 bits.
type FullAddress is (
    PASpace  paspace,
    core.bits(56) address
)
# ExceptionRecord
# ===============
type ExceptionRecord is (
    Exception   exceptype,           # Exception class
    core.bits(25)    syndrome,            # Syndrome record
    core.bits(24)    syndrome2,           # Syndrome record
    FullAddress paddress,            # Physical fault address
    core.bits(64)    vaddress,            # Virtual fault address
    boolean     ipavalid,            # Validity of Intermediate Physical fault address
    boolean     pavalid,             # Validity of Physical fault address
    bit         NS,                  # Intermediate Physical fault address space
    core.bits(56)    ipaddress,           # Intermediate Physical fault address
    boolean     trappedsyscallinst)  # Trapped SVC or SMC instruction
# core.ReportHypEntry()
# ========================
# Report syndrome information to Hyp mode registers.
core.ReportHypEntry(ExceptionRecord exception)
    Exception exceptype = exception.exceptype;
    (ec,il) = core.ExceptionClass(exceptype);
    iss  = exception.syndrome;
    iss2 = exception.syndrome2;
    # IL is not valid for Data Abort exceptions without valid instruction syndrome information
    if ec IN {0x24,0x25} and core.Bit(iss,24) == '0':
        il = '1';
    HSR = core.Field(ec,5,0):il:iss;
    if exceptype IN {Exception_InstructionAbort, Exception_PCAlignment}:
        HIFAR = core.Field(exception.vaddress,31,0);
        HDFAR = UNKNOWN = 0;
    elsif exceptype == Exception_DataAbort:
        HIFAR = UNKNOWN = 0;
        HDFAR = core.Field(exception.vaddress,31,0);
    if exception.ipavalid:
        HPFAR = core.SetField(HPFAR,31,4,core.Field(exception.ipaddress,39,12));
    else:
        HPFAR = core.SetField(HPFAR,31,4,UNKNOWN = 0);
    return;
constant core.bits(5) M32_User    = '10000';
constant core.bits(5) M32_FIQ     = '10001';
constant core.bits(5) M32_IRQ     = '10010';
constant core.bits(5) M32_Svc     = '10011';
constant core.bits(5) M32_Monitor = '10110';
constant core.bits(5) M32_Abort   = '10111';
constant core.bits(5) M32_Hyp     = '11010';
constant core.bits(5) M32_Undef   = '11011';
constant core.bits(5) M32_System  = '11111';
# core.BadMode()
# =========
boolean core.BadMode(core.bits(5) mode)
    # Return True if 'mode' encodes a mode that is not valid for this implementation
    valid = False;
    case mode of
        when M32_Monitor
            valid = core.HaveAArch32EL(EL3);
        when M32_Hyp
            valid = core.HaveAArch32EL(EL2);
        when M32_FIQ, M32_IRQ, M32_Svc, M32_Abort, M32_Undef, M32_System
            # If EL3 is implemented and using AArch32, then these modes are EL3 modes in Secure
            # state, and EL1 modes in Non-secure state. If EL3 is not implemented or is using
            # AArch64, then these modes are EL1 modes.
            # Therefore it is sufficient to test this implementation supports EL1 using AArch32.
            valid = core.HaveAArch32EL(EL1);
        when M32_User
            valid = core.HaveAArch32EL(EL0);
        otherwise
            valid = False;           # Passed an illegal mode value
    return not valid;
# core.HaveRME()
# =========
# Returns True if the Realm Management Extension is implemented, and False
# otherwise.
boolean core.HaveRME()
    return core.IsFeatureImplemented(FEAT_RME);
# core.HaveSecureState()
# =================
# Return True if Secure State is supported.
boolean core.HaveSecureState()
    if not core.HaveEL(EL3):
        return core.SecureOnlyImplementation();
    if core.HaveRME() and not core.HaveSecureEL2Ext():
        return False;
    return True;
# core.EffectiveSCR_EL3_NS()
# =====================
# Return Effective SCR_EL3.NS value.
bit core.EffectiveSCR_EL3_NS()
    if not core.HaveSecureState():
        return '1';
    elsif not core.HaveEL(EL3):
        return '0';
    else:
        return SCR_EL3.NS;
# core.EffectiveSCR_EL3_NSE()
# ======================
# Return Effective SCR_EL3.NSE value.
bit core.EffectiveSCR_EL3_NSE()
    return '0' if not core.HaveRME() else SCR_EL3.NSE;
# core.ELFromM32()
# ===========
(boolean,core.bits(2)) core.ELFromM32(core.bits(5) mode)
    # Convert an AArch32 mode encoding to an Exception level.
    # Returns (valid,EL):
    #   'valid' is True if 'core.Field(mode,4,0)' encodes a mode that is both valid for this implementation
    #           and the current value of SCR.NS/SCR_EL3.NS.
    #   'EL'    is the Exception level decoded from 'mode'.
    el = 0;
    boolean valid = not core.BadMode(mode);  # Check for modes that are not valid for this implementation
    core.bits(2) effective_nse_ns = core.EffectiveSCR_EL3_NSE() : core.EffectiveSCR_EL3_NS();
    case mode of
        when M32_Monitor
            el = EL3;
        when M32_Hyp
            el = EL2;
        when M32_FIQ, M32_IRQ, M32_Svc, M32_Abort, M32_Undef, M32_System
            # If EL3 is implemented and using AArch32, then these modes are EL3 modes in Secure
            # state, and EL1 modes in Non-secure state. If EL3 is not implemented or is using
            # AArch64, then these modes are EL1 modes.
            el = (EL3 if core.HaveEL(EL3) and not core.HaveAArch64() and SCR.NS == '0' else EL1);
        when M32_User
            el = EL0;
        otherwise
            valid = False;           # Passed an illegal mode value
    if valid and el == EL2 and core.HaveEL(EL3) and SCR_GEN[].NS == '0':
        valid = False;               # EL2 only valid in Non-secure state in AArch32
    elsif valid and core.HaveRME() and effective_nse_ns == '10':
        valid = False;               # Illegal Exception Return from EL3 if SCR_EL3.<NSE,NS>
                                     # selects a reserved encoding
    if not valid:
         el = UNKNOWN = 0;
    return (valid, el);
# core.WriteMode()
# ===================
# Function for dealing with writes to core.APSR.M from AArch32 state only.
# This ensures that core.APSR.EL and core.APSR.SP are always valid.
core.WriteMode(core.bits(5) mode)
    (valid,el) = core.ELFromM32(mode);
    assert valid;
    core.APSR.M   = mode;
    core.APSR.EL  = el;
    core.APSR.nRW = '1';
    core.APSR.SP  = ('0' if mode IN {M32_User,M32_System} else '1');
    return;
# SecurityState
# =============
# The Security state of an execution context
enumeration SecurityState {
    SS_NonSecure,
    SS_Root,
    SS_Realm,
    SS_Secure
};
# core.SecurityStateAtEL()
# ===================
# Returns the effective security state at the exception level based off current settings.
SecurityState core.SecurityStateAtEL(core.bits(2) EL)
    if core.HaveRME():
        if EL == EL3: return SS_Root;
        effective_nse_ns = SCR_EL3.NSE : core.EffectiveSCR_EL3_NS();
        case effective_nse_ns of
            when '00' return SS_Secure; if core.HaveSecureEL2Ext() else core.Unreachable();
            when '01' return SS_NonSecure;
            when '11' return SS_Realm;
            otherwise        core.Unreachable();
    if not core.HaveEL(EL3):
        if core.SecureOnlyImplementation():
            return SS_Secure;
        else:
            return SS_NonSecure;
    elsif EL == EL3:
        return SS_Secure;
    else:
        # For EL2 call only when EL2 is enabled in current security state
        core.assert(EL != EL2 or core.EL2Enabled());
        if not core.ELUsingAArch32(EL3):
            return SS_NonSecure if SCR_EL3.NS == '1' else SS_Secure;
        else:
            return SS_NonSecure if SCR.NS == '1' else SS_Secure;
# core.CurrentSecurityState()
# ======================
# Returns the effective security state at the exception level based off current settings.
SecurityState core.CurrentSecurityState()
    return core.SecurityStateAtEL(core.APSR.EL);
# core.EndOfInstruction()
# ==================
# Terminate processing of the current instruction.
core.EndOfInstruction();
# core.HaveSSBSExt()
# =============
# Returns True if support for SSBS is implemented, and False otherwise.
boolean core.HaveSSBSExt()
    return core.IsFeatureImplemented(FEAT_SSBS);
# core.UsingAArch32()
# ==============
# Return True if the current Exception level is using AArch32, False if using AArch64.
boolean core.UsingAArch32()
    boolean aarch32 = (core.APSR.nRW == '1');
    if not core.HaveAArch32():
         assert not aarch32;
    if not core.HaveAArch64():
         assert aarch32;
    return aarch32;
# SPSR[] - non-assignment form
# ============================
core.bits(N) SPSR[]
    core.bits(N) result;
    if core.UsingAArch32():
        assert N == 32;
        case core.APSR.M of
            when M32_FIQ      result = SPSR_fiq<N-1:0>;
            when M32_IRQ      result = SPSR_irq<N-1:0>;
            when M32_Svc      result = SPSR_svc<N-1:0>;
            when M32_Monitor  result = SPSR_mon<N-1:0>;
            when M32_Abort    result = SPSR_abt<N-1:0>;
            when M32_Hyp      result = SPSR_hyp<N-1:0>;
            when M32_Undef    result = SPSR_und<N-1:0>;
            otherwise         core.Unreachable();
    else:
        assert N == 64;
        case core.APSR.EL of
            when EL1          result = SPSR_EL1<N-1:0>;
            when EL2          result = SPSR_EL2<N-1:0>;
            when EL3          result = SPSR_EL3<N-1:0>;
            otherwise         core.Unreachable();
    return result;
# SPSR[] - assignment form
# ========================
SPSR[] = core.bits(N) value
    if core.UsingAArch32():
        assert N == 32;
        case core.APSR.M of
            when M32_FIQ      SPSR_fiq<N-1:0> = value<N-1:0>;
            when M32_IRQ      SPSR_irq<N-1:0> = value<N-1:0>;
            when M32_Svc      SPSR_svc<N-1:0> = value<N-1:0>;
            when M32_Monitor  SPSR_mon<N-1:0> = value<N-1:0>;
            when M32_Abort    SPSR_abt<N-1:0> = value<N-1:0>;
            when M32_Hyp      SPSR_hyp<N-1:0> = value<N-1:0>;
            when M32_Undef    SPSR_und<N-1:0> = value<N-1:0>;
            otherwise         core.Unreachable();
    else:
        assert N == 64;
        case core.APSR.EL of
            when EL1          SPSR_EL1<N-1:0> = value<N-1:0>;
            when EL2          SPSR_EL2<N-1:0> = value<N-1:0>;
            when EL3          SPSR_EL3<N-1:0> = value<N-1:0>;
            otherwise         core.Unreachable();
    return;
# core.SynchronizeContext()
# ====================
core.SynchronizeContext();
# core.Halted()
# ========
boolean core.Halted()
    return not (EDSCR.STATUS IN {'000001', '000010'});                     # Halted
# core.UpdateEDSCRFields()
# ===================
# Update EDSCR PE state fields
core.UpdateEDSCRFields()
    if not core.Halted():
        EDSCR.EL = '00';
        if core.HaveRME():
            EDSCR.<NSE,NS> = UNKNOWN = 0;
        else:
            EDSCR.NS = bit UNKNOWN;
        EDSCR.RW = '1111';
    else:
        EDSCR.EL = core.APSR.EL;
        ss = core.CurrentSecurityState();
        if core.HaveRME():
            case ss of
                when SS_Secure    EDSCR.<NSE,NS> = '00';
                when SS_NonSecure EDSCR.<NSE,NS> = '01';
                when SS_Root      EDSCR.<NSE,NS> = '10';
                when SS_Realm     EDSCR.<NSE,NS> = '11';
        else:
            EDSCR.NS = '0' if ss == SS_Secure else '1';
        RW = 0;
        RW = core.SetBit(RW,1,'0' if core.ELUsingAArch32(EL1) else '1')
        if core.APSR.EL != EL0:
            RW = core.SetBit(RW,0,core.Bit(RW,1))
        else:
            RW = core.SetBit(RW,0,'0' if core.UsingAArch32() else '1')
        if not core.HaveEL(EL2) or (core.HaveEL(EL3) and SCR_GEN[].NS == '0' and not core.IsSecureEL2Enabled()):
            RW = core.SetBit(RW,2,core.Bit(RW,1))
        else:
            RW = core.SetBit(RW,2,'0' if core.ELUsingAArch32(EL2) else '1')
        if not core.HaveEL(EL3):
            RW = core.SetBit(RW,3,core.Bit(RW,2))
        else:
            RW = core.SetBit(RW,3,'0' if core.ELUsingAArch32(EL3) else '1')
        # The least-significant bits of EDSCR.RW are UNKNOWN if any higher EL is using AArch32.
        if core.Bit(RW,3) == '0':
             RW = core.SetField(RW,2,0,UNKNOWN = 0);
        elsif core.Bit(RW,2) == '0':
     RW = core.SetField(RW,1,0,UNKNOWN = 0);
        elsif core.Bit(RW,1) == '0':
     RW = core.SetBit(RW,0,bit UNKNOWN)
        EDSCR.RW = RW;
    return;
# core.EnterHypModeInDebugState()
# ==================================
# Take an exception in Debug state to Hyp mode.
core.EnterHypModeInDebugState(ExceptionRecord exception)
    core.SynchronizeContext();
    assert core.HaveEL(EL2) and core.CurrentSecurityState() == SS_NonSecure and core.ELUsingAArch32(EL2);
    core.ReportHypEntry(exception);
    core.WriteMode(M32_Hyp);
    SPSR[] = UNKNOWN = 0;
    ELR_hyp = UNKNOWN = 0;
    # In Debug state, the PE always execute T32 instructions when in AArch32 state, and
    # core.APSR.{SS,A,I,F} are not observable so behave as UNKNOWN.
    core.APSR.T = '1';                             # core.APSR.J is RES0
    core.APSR.<SS,A,I,F> = UNKNOWN = 0;
    DLR = UNKNOWN = 0;
    DSPSR = UNKNOWN = 0;
    core.APSR.E = HSCTLR.EE;
    core.APSR.IL = '0';
    core.APSR.IT = '00000000';
    if core.HaveSSBSExt():
         core.APSR.SSBS = bit UNKNOWN;
    EDSCR.ERR = '1';
    core.UpdateEDSCRFields();
    core.EndOfInstruction();
# ExceptionalOccurrenceTargetState
# ================================
# Enumeration to represent the target state of an Exceptional Occurrence.
# The Exceptional Occurrence can be either Exception or Debug State entry.
enumeration ExceptionalOccurrenceTargetState {
    AArch32_NonDebugState,
    AArch64_NonDebugState,
    DebugState
};
# core.ELIsInHost()
# ============
boolean core.ELIsInHost(core.bits(2) el)
    if not core.HaveVirtHostExt() or core.ELUsingAArch32(EL2):
        return False;
    case el of
        when EL3
            return False;
        when EL2
            return core.EL2Enabled() and HCR_EL2.E2H == '1';
        when EL1
            return False;
        when EL0
            return core.EL2Enabled() and HCR_EL2.<E2H,TGE> == '11';
        otherwise
            core.Unreachable();
# core.HavePACExt()
# ============
# Returns True if support for the PAC extension is implemented, False otherwise.
boolean core.HavePACExt()
    return core.IsFeatureImplemented(FEAT_PAuth);
# core.S1TranslationRegime()
# =====================
# Stage 1 translation regime for the given Exception level
core.bits(2) core.S1TranslationRegime(core.bits(2) el)
    if el != EL0:
        return el;
    elsif core.HaveEL(EL3) and core.ELUsingAArch32(EL3) and SCR.NS == '0':
        return EL3;
    elsif core.HaveVirtHostExt() and core.ELIsInHost(el):
        return EL2;
    else:
        return EL1;
# core.S1TranslationRegime()
# =====================
# Returns the Exception level controlling the current Stage 1 translation regime. For the most
# part this is unused in code because the System register accessors (SCTLR[], etc.) implicitly
# return the correct value.
core.bits(2) core.S1TranslationRegime()
    return core.S1TranslationRegime(core.APSR.EL);
# core.EffectiveTBI()
# ==============
# Returns the effective TBI in the AArch64 stage 1 translation regime for "el".
bit core.EffectiveTBI(core.bits(64) address, boolean IsInstr, core.bits(2) el)
    bit tbi;
    bit tbid;
    assert core.HaveEL(el);
    regime = core.S1TranslationRegime(el);
    core.assert(not core.ELUsingAArch32(regime));
    case regime of
        when EL1
            tbi = TCR_EL1.TBI1 if core.Bit(address,55) == '1' else TCR_EL1.TBI0;
            if core.HavePACExt():
                tbid = TCR_EL1.TBID1 if core.Bit(address,55) == '1' else TCR_EL1.TBID0;
        when EL2
            if core.HaveVirtHostExt() and core.ELIsInHost(el):
                tbi = TCR_EL2.TBI1 if core.Bit(address,55) == '1' else TCR_EL2.TBI0;
                if core.HavePACExt():
                    tbid = TCR_EL2.TBID1 if core.Bit(address,55) == '1' else TCR_EL2.TBID0;
            else:
                tbi = TCR_EL2.TBI;
                if core.HavePACExt():
                     tbid = TCR_EL2.TBID;
        when EL3
            tbi = TCR_EL3.TBI;
            if core.HavePACExt():
                 tbid = TCR_EL3.TBID;
    return ('1' if tbi == '1' and (not core.HavePACExt() or tbid == '0' or not IsInstr) else '0');
# core.AddrTop()
# =========
# Return the MSB number of a virtual address in the stage 1 translation regime for "el".
# If EL1 is using AArch64 then addresses from EL0 using AArch32 are zero-extended to 64 bits.
integer core.AddrTop(core.bits(64) address, boolean IsInstr, core.bits(2) el)
    assert core.HaveEL(el);
    regime = core.S1TranslationRegime(el);
    if core.ELUsingAArch32(regime):
        # AArch32 translation regime.
        return 31;
    else:
        if core.EffectiveTBI(address, IsInstr, el) == '1':
            return 55;
        else:
            return 63;
# core.IsInHost()
# ==========
boolean core.IsInHost()
    return core.ELIsInHost(core.APSR.EL);
# core.SignExtend()
# ============
core.bits(N) core.SignExtend(core.bits(M) x, integer N)
    assert N >= M;
    return core.Replicate(x<M-1>, N-M) : x;
# AArch64.core.BranchAddr()
# ====================
# Return the virtual address with tag bits removed.
# This is typically used when the address will be stored to the program counter.
core.bits(64) AArch64.core.BranchAddr(core.bits(64) vaddress, core.bits(2) el)
    assert not core.UsingAArch32();
    msbit = core.AddrTop(vaddress, True, el);
    if msbit == 63:
        return vaddress;
    elsif (el IN {EL0, EL1} or core.IsInHost()) and vaddress<msbit> == '1':
        return core.SignExtend(vaddress<msbit:0>, 64);
    else:
        return core.ZeroExtend(vaddress<msbit:0>, 64);
# core.BRBEMispredictAllowed()
# =======================
# Returns True if the recording of branch misprediction is allowed, False otherwise.
boolean core.BRBEMispredictAllowed()
    if core.EL2Enabled() and BRBCR_EL2.MPRED == '0':
         return False;
    if BRBCR_EL1.MPRED == '0':
         return False;
    return True;
# core.BranchEncCycleCount()
# =====================
# The first return result is '1' if either of the following is true, and '0' otherwise:
# - This is the first Branch record after the PE exited a Prohibited Region.
# - This is the first Branch record after cycle counting has been enabled.
# If the first return return is '0', the second return result is the encoded cycle count
# since the last branch.
# The format of this field uses a mantissa and exponent to express the cycle count value.
#  - bits[7:0] indicate the mantissa M.
#  - bits[13:8] indicate the exponent E.
# The cycle count is expressed using the following function:
#   cycle_count = (core.UInt(M) if core.IsZero(E) else core.UInt('1':M:core.Zeros(core.UInt(E)-1)))
# A value of all ones in both the mantissa and exponent indicates the cycle count value
# exceeded the size of the cycle counter.
# If the cycle count is not known, the second return result is zero.
(bit, core.bits(14)) core.BranchEncCycleCount();
# core.BranchMispredict()
# ==================
# Returns True if the branch being executed was mispredicted, False otherwise.
boolean core.BranchMispredict();
# core.HaveBRBEv1p1()
# ==============
# Returns True if BRBEv1p1 extension is implemented, and False otherwise.
boolean core.HaveBRBEv1p1()
    return core.IsFeatureImplemented(FEAT_BRBEv1p1);
# core.BranchRecordAllowed()
# =====================
# Returns True if branch recording is allowed, False otherwise.
boolean core.BranchRecordAllowed(core.bits(2) el)
    if core.ELUsingAArch32(el):
        return False;
    if BRBFCR_EL1.PAUSED == '1':
        return False;
    if el == EL3 and core.HaveBRBEv1p1():
        return (MDCR_EL3.E3BREC != MDCR_EL3.E3BREW);
    if core.HaveEL(EL3) and (MDCR_EL3.SBRBE == '00' or
        (core.CurrentSecurityState() == SS_Secure and MDCR_EL3.SBRBE == '01')) then
        return False;
    case el of
        when EL3  return False;                # FEAT_BRBEv1p1 not implemented
        when EL2  return BRBCR_EL2.E2BRE == '1';
        when EL1  return BRBCR_EL1.E1BRE == '1';
        when EL0
            if core.EL2Enabled() and HCR_EL2.TGE == '1':
                return BRBCR_EL2.E0HBRE == '1';
            else:
                return BRBCR_EL1.E0BRE == '1';
# BranchType
# ==========
# Information associated with a change in control flow.
enumeration BranchType {
    'DIRCALL',     # Direct Branch with link
    'INDCALL',     # Indirect Branch with link
    'ERET',        # Exception return (indirect)
    'DBGEXIT',     # Exit from Debug state
    'RET',         # Indirect branch with function return hint
    'DIR',         # Direct branch
    'INDIR',       # Indirect branch
    'EXCEPTION',   # Exception entry
    'TMFAIL',      # Transaction failure
    'RESET',       # Reset
    'UNKNOWN'};   # Other
# core.FilterBranchRecord()
# ====================
# Returns True if the branch record is not filtered out, False otherwise.
boolean core.FilterBranchRecord(BranchType br, boolean cond)
    case br of
        when 'DIRCALL'
            return BRBFCR_EL1.DIRCALL != BRBFCR_EL1.EnI;
        when 'INDCALL'
            return BRBFCR_EL1.INDCALL != BRBFCR_EL1.EnI;
        when 'RET'
            return BRBFCR_EL1.RTN != BRBFCR_EL1.EnI;
        when 'DIR'
            if cond:
                return BRBFCR_EL1.CONDDIR != BRBFCR_EL1.EnI;
            else:
                return BRBFCR_EL1.DIRECT != BRBFCR_EL1.EnI;
        when 'INDIR'
            return BRBFCR_EL1.INDIRECT != BRBFCR_EL1.EnI;
        otherwise  core.Unreachable();
    return False;
# core.HaveTME()
# =========
boolean core.HaveTME()
    return core.IsFeatureImplemented(FEAT_TME);
_PC = 0;
# PC - non-assignment form
# ========================
# Read program counter.
core.bits(64) PC[]
    return _PC;
# core.GetNumEventCounters()
# =====================
# Returns the number of event counters implemented. This is indicated to software at the
# highest Exception level by PMCR.N in AArch32 state, and PMCR_EL0.N in AArch64 state.
integer core.GetNumEventCounters()
    return integer IMPLEMENTATION_DEFINED "Number of event counters";
# core.HavePMUv3()
# ===========
# Returns True if the Performance Monitors extension is implemented, and False otherwise.
boolean core.HavePMUv3()
    return core.IsFeatureImplemented(FEAT_PMUv3);
# core.HavePMUv3ICNTR()
# ================
# Returns True if support for the Fixed-function instruction counter is
# implemented, and False otherwise.
boolean core.HavePMUv3ICNTR()
    return core.IsFeatureImplemented(FEAT_PMUv3_ICNTR);
constant integer CYCLE_COUNTER_ID = 31;
signal DBGEN;
signal NIDEN;
signal SPIDEN;
signal SPNIDEN;
signal RLPIDEN;
signal RTPIDEN;
# core.ExternalInvasiveDebugEnabled()
# ==============================
# The definition of this function is IMPLEMENTATION DEFINED.
# In the recommended interface, this function returns the state of the DBGEN signal.
boolean core.ExternalInvasiveDebugEnabled()
    return DBGEN == HIGH;
# core.HaveNoninvasiveDebugAuth()
# ==========================
# Returns True if the Non-invasive debug controls are implemented.
boolean core.HaveNoninvasiveDebugAuth()
    return not core.IsFeatureImplemented(FEAT_Debugv8p4);
# core.ExternalNoninvasiveDebugEnabled()
# =================================
# This function returns True if the FEAT_Debugv8p4 is implemented.
# Otherwise, this function is IMPLEMENTATION DEFINED, and, in the
# recommended interface, ExternalNoninvasiveDebugEnabled returns
# the state of the (DBGEN | NIDEN) signal.
boolean core.ExternalNoninvasiveDebugEnabled()
    return not core.HaveNoninvasiveDebugAuth() or core.ExternalInvasiveDebugEnabled() or NIDEN == HIGH;
# core.ExternalSecureInvasiveDebugEnabled()
# ====================================
# The definition of this function is IMPLEMENTATION DEFINED.
# In the recommended interface, this function returns the state of the (DBGEN & SPIDEN) signal.
# CoreSight allows asserting SPIDEN without also asserting DBGEN, but this is not recommended.
boolean core.ExternalSecureInvasiveDebugEnabled()
    if not core.HaveEL(EL3) and not core.SecureOnlyImplementation():
         return False;
    return core.ExternalInvasiveDebugEnabled() and SPIDEN == HIGH;
# core.ExternalSecureNoninvasiveDebugEnabled()
# =======================================
# This function returns the value of core.ExternalSecureInvasiveDebugEnabled() when FEAT_Debugv8p4
# is implemented. Otherwise, the definition of this function is IMPLEMENTATION DEFINED.
# In the recommended interface, this function returns the state of the (DBGEN | NIDEN) &
# (SPIDEN | SPNIDEN) signal.
boolean core.ExternalSecureNoninvasiveDebugEnabled()
    if not core.HaveEL(EL3) and not core.SecureOnlyImplementation():
         return False;
    if core.HaveNoninvasiveDebugAuth():
        return core.ExternalNoninvasiveDebugEnabled() and (SPIDEN == HIGH or SPNIDEN == HIGH);
    else:
        return core.ExternalSecureInvasiveDebugEnabled();
# core.HaveHPMDExt()
# =============
boolean core.HaveHPMDExt()
    return core.IsFeatureImplemented(FEAT_PMUv3p1);
# core.HaveNoSecurePMUDisableOverride()
# ================================
boolean core.HaveNoSecurePMUDisableOverride()
    return core.IsFeatureImplemented(FEAT_Debugv8p2);
# core.HavePMUv3p5()
# =============
# Returns True if the PMUv3.5 extension is implemented, and False otherwise.
boolean core.HavePMUv3p5()
    return core.IsFeatureImplemented(FEAT_PMUv3p5);
# core.HavePMUv3p7()
# =============
# Returns True if the PMUv3.7 extension is implemented, and False otherwise.
boolean core.HavePMUv3p7()
    return core.IsFeatureImplemented(FEAT_PMUv3p7);
constant integer INSTRUCTION_COUNTER_ID = 32;
# core.IsZero()
# ========
boolean core.IsZero(core.bits(N) x)
    return x == core.Zeros(N);
# Unpredictable
# =============
# List of Constrained Unpredictable situations.
enumeration Unpredictable {
                           # VMSR on MVFR
                           Unpredictable_VMSR,
                           # Writeback/transfer register overlap (load)
                           Unpredictable_WBOVERLAPLD,
                           # Writeback/transfer register overlap (store)
                           Unpredictable_WBOVERLAPST,
                           # Load Pair transfer register overlap
                           Unpredictable_LDPOVERLAP,
                           # Store-exclusive base/status register overlap
                           Unpredictable_BASEOVERLAP,
                           # Store-exclusive data/status register overlap
                           Unpredictable_DATAOVERLAP,
                           # Load-store alignment checks
                           Unpredictable_DEVPAGE2,
                           # Instruction fetch from Device memory
                           Unpredictable_INSTRDEVICE,
                           # Reserved CPACR value
                           Unpredictable_RESCPACR,
                           # Reserved MAIR value
                           Unpredictable_RESMAIR,
                           # Effect of SCTLR_ELx.C on Tagged attribute
                           Unpredictable_S1CTAGGED,
                           # Reserved Stage 2 MemAttr value
                           Unpredictable_S2RESMEMATTR,
                           # Reserved TEX:C:B value
                           Unpredictable_RESTEXCB,
                           # Reserved PRRR value
                           Unpredictable_RESPRRR,
                           # Reserved DACR field
                           Unpredictable_RESDACR,
                           # Reserved VTCR.S value
                           Unpredictable_RESVTCRS,
                           # Reserved TCR.TnSZ value
                           Unpredictable_RESTnSZ,
                           # Reserved SCTLR_ELx.TCF value
                           Unpredictable_RESTCF,
                           # Tag stored to Device memory
                           Unpredictable_DEVICETAGSTORE,
                           # Out-of-range TCR.TnSZ value
                           Unpredictable_OORTnSZ,
                           # IPA size exceeds PA size
                           Unpredictable_LARGEIPA,
                           # Syndrome for a known-passing conditional A32 instruction
                           Unpredictable_ESRCONDPASS,
                           # Illegal State exception: zero core.APSR.IT
                           Unpredictable_ILZEROIT,
                           # Illegal State exception: zero core.APSR.T
                           Unpredictable_ILZEROT,
                           # Debug: prioritization of Vector Catch
                           Unpredictable_BPVECTORCATCHPRI,
                           # Debug Vector Catch: match on 2nd halfword
                           Unpredictable_VCMATCHHALF,
                           # Debug Vector Catch: match on Data Abort
                           # or Prefetch abort
                           Unpredictable_VCMATCHDAPA,
                           # Debug watchpoints: non-zero MASK and non-ones BAS
                           Unpredictable_WPMASK&BAS,
                           # Debug watchpoints: non-contiguous BAS
                           Unpredictable_WPBASCONTIGUOUS,
                           # Debug watchpoints: reserved MASK
                           Unpredictable_RESWPMASK,
                           # Debug watchpoints: non-zero MASKed bits of address
                           Unpredictable_WPMASKEDBITS,
                           # Debug breakpoints and watchpoints: reserved control bits
                           Unpredictable_RESBPWPCTRL,
                           # Debug breakpoints: not implemented
                           Unpredictable_BPNOTIMPL,
                           # Debug breakpoints: reserved type1
                           Unpredictable_RESBPTYPE,
                           # Debug breakpoints: not-context-aware breakpoint
                           Unpredictable_BPNOTCTXCMP,
                           # Debug breakpoints: match on 2nd halfword of instruction
                           Unpredictable_BPMATCHHALF,
                           # Debug breakpoints: mismatch on 2nd halfword of instruction
                           Unpredictable_BPMISMATCHHALF,
                           # Debug: restart to a misaligned AArch32 PC value
                           Unpredictable_RESTARTALIGNPC,
                           # Debug: restart to a not-zero-extended AArch32 PC value
                           Unpredictable_RESTARTZEROUPPERPC,
                           # Zero top 32 bits of X registers in AArch32 state
                           Unpredictable_ZEROUPPER,
                           # Zero top 32 bits of PC on illegal return to
                           # AArch32 state
                           Unpredictable_ERETZEROUPPERPC,
                           # Force address to be aligned when interworking
                           # branch to A32 state
                           Unpredictable_A32FORCEALIGNPC,
                           # SMC disabled
                           Unpredictable_SMD,
                           # FF speculation
                           Unpredictable_NONFAULT,
                           # Zero top bits of Z registers in EL change
                           Unpredictable_SVEZEROUPPER,
                           # Load mem data in NF loads
                           Unpredictable_SVELDNFDATA,
                           # Write zeros in NF loads
                           Unpredictable_SVELDNFZERO,
                           # SP alignment fault when predicate is all zero
                           Unpredictable_CHECKSPNONEACTIVE,
                           # Zero top bits of ZA registers in EL change
                           Unpredictable_SMEZEROUPPER,
                           # HCR_EL2.<NV,NV1> == '01'
                           Unpredictable_NVNV1,
                           # Reserved shareability encoding
                           Unpredictable_Shareability,
                           # Access Flag Update by HW
                           Unpredictable_AFUPDATE,
                           # Dirty Bit State Update by HW
                           Unpredictable_DBUPDATE,
                           # Consider SCTLR[].IESB in Debug state
                           Unpredictable_IESBinDebug,
                           # Bad settings for PMSFCR_EL1/PMSEVFR_EL1/PMSLATFR_EL1
                           Unpredictable_BADPMSFCR,
                           # Zero saved BType value in SPSR_ELx/DPSR_EL0
                           Unpredictable_ZEROBTYPE,
                           # Timestamp constrained to virtual or physical
                           Unpredictable_EL2TIMESTAMP,
                           Unpredictable_EL1TIMESTAMP,
                            # Reserved MDCR_EL3.<NSTBE,NSTB> or MDCR_EL3.<NSPBE,NSPB> value
                            Unpredictable_RESERVEDNSxB,
                           # WFET or WFIT instruction in Debug state
                           Unpredictable_WFxTDEBUG,
                           # Address does not support LS64 instructions
                           Unpredictable_LS64UNSUPPORTED,
                           # Misaligned exclusives, atomics, acquire/release
                           # to region that is not Normal Cacheable WB
                           Unpredictable_MISALIGNEDATOMIC,
                           # Clearing DCC/ITR sticky flags when instruction is in flight
                           Unpredictable_CLEARERRITEZERO,
                           # ALUEXCEPTIONRETURN when in user/system mode in
                           # A32 instructions
                           Unpredictable_ALUEXCEPTIONRETURN,
                           # Trap to register in debug state are ignored
                           Unpredictable_IGNORETRAPINDEBUG,
                           # Compare DBGBVR.RESS for BP/WP
                           Unpredictable_DBGxVR_RESS,
                           # Inaccessible event counter
                           Unpredictable_PMUEVENTCOUNTER,
                           # Reserved PMSCR.PCT behavior.
                           Unpredictable_PMSCR_PCT,
                           # MDCR_EL2.HPMN or HDCR.HPMN is larger than PMCR.N or
                           # FEAT_HPMN0 is not implemented and HPMN is 0.
                           Unpredictable_CounterReservedForEL2,
                           # Generate BRB_FILTRATE event on BRB injection
                           Unpredictable_BRBFILTRATE,
                          # Operands for CPY*/SET* instructions overlap or
                          # use 0b11111 as a register specifier
                          Unpredictable_MOPSOVERLAP31,
                          # Store-only Tag checking on a failed Atomic Compare and Swap
                          Unpredictable_STOREONLYTAGCHECKEDCAS,
                           # Reserved PMEVTYPER<n>_EL0.TC value
                           Unpredictable_RESTC
};
# core.ConstrainUnpredictableBool()
# ============================
# This is a variant of the ConstrainUnpredictable function where the result is either
# Constraint_True or Constraint_False.
boolean core.ConstrainUnpredictableBool(Unpredictable which);
# core.HaveFeatHPMN0()
# ===============
# Returns True if HDCR.HPMN or MDCR_EL2.HPMN is permitted to be 0 without
# generating raise Exception('UNPREDICTABLE') behavior, and False otherwise.
boolean core.HaveFeatHPMN0()
    return core.IsFeatureImplemented(FEAT_HPMN0);
# core.UInt()
# ======
integer core.UInt(core.bits(N) x)
    result = 0;
    for i = 0 to N-1
        if x<i> == '1':
             result = result + 2^i;
    return result;
# core.PMUCounterIsHyp()
# =================
# Returns True if a counter is reserved for use by EL2, False otherwise.
boolean core.PMUCounterIsHyp(integer n)
    if n == INSTRUCTION_COUNTER_ID:
         return False;
    if n == CYCLE_COUNTER_ID:
         return False;
    resvd_for_el2 = False;
    if core.HaveEL(EL2):
             # Software can reserve some event counters for EL2
        core.bits(5) hpmn_bits = MDCR_EL2.HPMN if core.HaveAArch64() else HDCR.HPMN;
        resvd_for_el2 = n >= core.UInt(hpmn_bits);
        if core.UInt(hpmn_bits) > core.GetNumEventCounters() or (not core.HaveFeatHPMN0() and core.IsZero(hpmn_bits)):
            resvd_for_el2 = core.ConstrainUnpredictableBool(Unpredictable_CounterReservedForEL2);
    else:
        resvd_for_el2 = False;
    return resvd_for_el2;
# core.PMUOverflowCondition()
# ======================
# Checks for PMU overflow under certain parameter conditions
# If 'check_e' is True, then check the applicable one of PMCR_EL0.E and MDCR_EL2.HPME.
# If 'check_cnten' is True, then check the applicable PMCNTENCLR_EL0 bit.
# If 'check_cnten' is True, then check the applicable PMINTENCLR_EL1 bit.
# If 'include_lo' is True, then check counters in the set [0..(HPMN-1)], CCNTR
#     and ICNTR, unless excluded by other flags.
# If 'include_hi' is True, then check counters in the set [HPMN..(N-1)].
# If 'exclude_cyc' is True, then CCNTR is NOT checked.
# If 'exclude_sync' is True, then counters in synchronous mode are NOT checked.
boolean core.PMUOverflowCondition(boolean check_e, boolean check_cnten,
                             boolean check_inten,
                             boolean include_hi, boolean include_lo,
                             boolean exclude_cyc, boolean exclude_sync)
    integer counters = core.GetNumEventCounters();
    ovsf = 0;
    if core.HaveAArch64():
        ovsf = PMOVSCLR_EL0;
        # Remove unimplemented counters - these fields are RES0
        ovsf = core.SetField(ovsf,63,33,core.Zeros(31));
        if not core.HavePMUv3ICNTR():
            ovsf<INSTRUCTION_COUNTER_ID> = '0';
    else:
        ovsf = core.ZeroExtend(PMOVSR, 64);
    if counters < 31:
        ovsf<30:counters> = core.Zeros(31-counters);
    for idx = 0 to counters - 1
        bit E;
        boolean is_hyp = core.PMUCounterIsHyp(idx);
        if core.HaveAArch64():
            E = (MDCR_EL2.HPME if is_hyp else PMCR_EL0.E);
        else:
            E = (HDCR.HPME if is_hyp else PMCR.E);
        if check_e:
            ovsf<idx> = ovsf<idx> & E;
        if (not is_hyp and not include_lo) or (is_hyp and not include_hi):
            ovsf<idx> = '0';
    # Cycle counter
    if exclude_cyc or not include_lo:
        ovsf<CYCLE_COUNTER_ID> = '0';
    if check_e:
        ovsf<CYCLE_COUNTER_ID> = ovsf<CYCLE_COUNTER_ID> & PMCR_EL0.E;
    # Instruction counter
    if core.HaveAArch64() and core.HavePMUv3ICNTR():
        if not include_lo:
            ovsf<INSTRUCTION_COUNTER_ID> = '0';
        if check_e:
            ovsf<INSTRUCTION_COUNTER_ID> = ovsf<INSTRUCTION_COUNTER_ID> & PMCR_EL0.E;
    if check_cnten:
        core.bits(64) cnten = PMCNTENCLR_EL0 if core.HaveAArch64() else core.ZeroExtend(PMCNTENCLR, 64);
        ovsf = ovsf & cnten;
    if check_inten:
        core.bits(64) inten = PMINTENCLR_EL1 if core.HaveAArch64() else core.ZeroExtend(PMINTENCLR, 64);
        ovsf = ovsf & inten;
    return not core.IsZero(ovsf);
# core.HiLoPMUOverflow()
# =================
boolean core.HiLoPMUOverflow(boolean resvd_for_el2)
    boolean check_cnten  = False;
    boolean check_e      = False;
    boolean check_inten  = False;
    boolean include_lo   = not resvd_for_el2;
    boolean include_hi   = resvd_for_el2;
    boolean exclude_cyc  = False;
    boolean exclude_sync = False;
    boolean overflow = core.PMUOverflowCondition(check_e, check_cnten, check_inten,
                                            include_hi, include_lo,
                                            exclude_cyc, exclude_sync);
    return overflow;
# core.CountPMUEvents()
# ================
# Return True if counter "idx" should count its event.
# For the cycle counter, idx == CYCLE_COUNTER_ID (32).
# For the instruction counter, idx == INSTRUCTION_COUNTER_ID (33).
boolean core.CountPMUEvents(integer idx)
    constant integer num_counters = core.GetNumEventCounters();
    assert (idx == CYCLE_COUNTER_ID or idx < num_counters or
            (idx == INSTRUCTION_COUNTER_ID and core.HavePMUv3ICNTR()));
    debug = False;
    enabled = False;
    prohibited = False;
    filtered = False;
    frozen = False;
    resvd_for_el2 = False;
    bit E;
    bit spme;
    ovflws = 0;
    # Event counting is disabled in Debug state
    debug = core.Halted();
    # Software can reserve some counters for EL2
    resvd_for_el2 = core.PMUCounterIsHyp(idx);
    ss = core.CurrentSecurityState();
    # Main enable controls
    case idx of
        when INSTRUCTION_COUNTER_ID
            assert core.HaveAArch64();
            enabled = PMCR_EL0.E == '1' and PMCNTENSET_EL0.F0 == '1';
        when CYCLE_COUNTER_ID
            if core.HaveAArch64():
                enabled = PMCR_EL0.E == '1' and PMCNTENSET_EL0.C == '1';
            else:
                enabled = PMCR.E == '1' and PMCNTENSET.C == '1';
        otherwise
            if resvd_for_el2:
                E = MDCR_EL2.HPME if core.HaveAArch64() else HDCR.HPME;
            else:
                E = PMCR_EL0.E if core.HaveAArch64() else PMCR.E;
            if core.HaveAArch64():
                enabled = E == '1' and PMCNTENSET_EL0<idx> == '1';
            else:
                enabled = E == '1' and PMCNTENSET<idx> == '1';
    # Event counting is allowed unless it is prohibited by any rule below
    prohibited = False;
    # Event counting in Secure state is prohibited if all of:
    # * EL3 is implemented
    # * One of the following is true:
    #   - EL3 is using AArch64, MDCR_EL3.SPME == 0, and either:
    #     - FEAT_PMUv3p7 is not implemented
    #     - MDCR_EL3.MPMX == 0
    #   - EL3 is using AArch32 and SDCR.SPME == 0
    # * Executing at EL0 using AArch32 and one of the following is true:
    #     - EL3 is using AArch32 and SDER.SUNIDEN == 0
    #     - EL3 is using AArch64, EL1 is using AArch32, and SDER32_EL3.SUNIDEN == 0
    if core.HaveEL(EL3) and ss == SS_Secure:
        if not core.ELUsingAArch32(EL3):
            prohibited = MDCR_EL3.SPME == '0' and core.HavePMUv3p7() and MDCR_EL3.MPMX == '0';
        else:
            prohibited = SDCR.SPME == '0';
        if prohibited and core.APSR.EL == EL0:
            if core.ELUsingAArch32(EL3):
                prohibited = SDER.SUNIDEN == '0';
            elsif core.ELUsingAArch32(EL1):
                prohibited = SDER32_EL3.SUNIDEN == '0';
    # Event counting at EL3 is prohibited if all of:
    # * FEAT_PMUv3p7 is implemented
    # * EL3 is using AArch64
    # * One of the following is true:
    #   - MDCR_EL3.SPME == 0
    #   - PMNx is not reserved for EL2
    # * MDCR_EL3.MPMX == 1
    if not prohibited and core.HavePMUv3p7() and core.APSR.EL == EL3 and core.HaveAArch64():
        prohibited = MDCR_EL3.MPMX == '1' and (MDCR_EL3.SPME == '0' or not resvd_for_el2);
    # Event counting at EL2 is prohibited if all of:
    # * The HPMD Extension is implemented
    # * PMNx is not reserved for EL2
    # * EL2 is using AArch64 and MDCR_EL2.HPMD == 1 or EL2 is using AArch32 and HDCR.HPMD == 1
    if not prohibited and core.APSR.EL == EL2 and core.HaveHPMDExt() and not resvd_for_el2:
        hpmd = MDCR_EL2.HPMD if core.HaveAArch64() else HDCR.HPMD;
        prohibited = hpmd == '1';
    # The IMPLEMENTATION DEFINED authentication interface might override software
    if prohibited and not core.HaveNoSecurePMUDisableOverride():
        prohibited = not core.ExternalSecureNoninvasiveDebugEnabled();
    # Event counting might be frozen
    frozen = False;
    # If FEAT_PMUv3p7 is implemented, event counting can be frozen
    if core.HavePMUv3p7():
        bit FZ;
        if resvd_for_el2:
            FZ = MDCR_EL2.HPMFZO if core.HaveAArch64() else HDCR.HPMFZO;
        else:
            FZ = PMCR_EL0.FZO if core.HaveAArch64() else PMCR.FZO;
        frozen = (FZ == '1') and core.HiLoPMUOverflow(resvd_for_el2);
    # PMCR_EL0.DP or PMCR.DP disables the cycle counter when event counting is prohibited
    if (prohibited or frozen) and idx == CYCLE_COUNTER_ID:
        dp = PMCR_EL0.DP if core.HaveAArch64() else PMCR.DP;
        enabled = enabled and dp == '0';
        # Otherwise whether event counting is prohibited does not affect the cycle counter
        prohibited = False;
        frozen = False;
    # Freeze-on-SPE event is not implemented.
    # If FEAT_PMUv3p5 is implemented, cycle counting can be prohibited.
    # This is not overridden by PMCR_EL0.DP.
    if core.HavePMUv3p5() and idx == CYCLE_COUNTER_ID:
        if core.HaveEL(EL3) and ss == SS_Secure:
            sccd = MDCR_EL3.SCCD if core.HaveAArch64() else SDCR.SCCD;
            if sccd == '1':
                prohibited = True;
        if core.APSR.EL == EL2:
            hccd = MDCR_EL2.HCCD if core.HaveAArch64() else HDCR.HCCD;
            if hccd == '1':
                prohibited = True;
    # If FEAT_PMUv3p7 is implemented, cycle counting an be prohibited at EL3.
    # This is not overriden by PMCR_EL0.DP.
    if core.HavePMUv3p7() and idx == CYCLE_COUNTER_ID:
        if core.APSR.EL == EL3 and core.HaveAArch64() and MDCR_EL3.MCCD == '1':
            prohibited = True;
    # Event counting can be filtered by the {P, U, NSK, NSU, NSH, M, SH, RLK, RLU, RLH} bits
    filter = 0;
    case idx of
        when INSTRUCTION_COUNTER_ID
            filter = core.Field(PMICFILTR_EL0,31,0);
        when CYCLE_COUNTER_ID
            filter = core.Field(PMCCFILTR_EL0,31,0) if core.HaveAArch64() else PMCCFILTR;
        otherwise
            filter = core.Field(PMEVTYPER_EL0[idx],31,0) if core.HaveAArch64() else PMEVTYPEcore.readR(idx);
    P   = core.Bit(filter,31);
    U   = core.Bit(filter,30);
    NSK = core.Bit(filter,29) if core.HaveEL(EL3) else '0';
    NSU = core.Bit(filter,28) if core.HaveEL(EL3) else '0';
    NSH = core.Bit(filter,27) if core.HaveEL(EL2) else '0';
    M   = core.Bit(filter,26) if core.HaveEL(EL3) and core.HaveAArch64() else '0';
    SH  = core.Bit(filter,24) if core.HaveEL(EL3) and core.HaveSecureEL2Ext() else '0';
    RLK = core.Bit(filter,22) if core.HaveRME() else '0';
    RLU = core.Bit(filter,21) if core.HaveRME() else '0';
    RLH = core.Bit(filter,20) if core.HaveRME() else '0';
    ss = core.CurrentSecurityState();
    case core.APSR.EL of
        when EL0
            case ss of
                when SS_NonSecure filtered = U != NSU;
                when SS_Secure    filtered = U == '1';
                when SS_Realm     filtered = U != RLU;
        when EL1
            case ss of
                when SS_NonSecure filtered = P != NSK;
                when SS_Secure    filtered = P == '1';
                when SS_Realm     filtered = P != RLK;
        when EL2
            case ss of
                when SS_NonSecure filtered = NSH == '0';
                when SS_Secure    filtered = NSH == SH;
                when SS_Realm     filtered = NSH == RLH;
        when EL3
            if core.HaveAArch64():
                filtered = M != P;
            else:
                filtered = P == '1';
    return not debug and enabled and not prohibited and not filtered and not frozen;
# core.IncrementInstructionCounter()
# =============================
# Increment the instruction counter and possibly set overflow bits.
core.IncrementInstructionCounter(integer increment)
    if core.CountPMUEvents(INSTRUCTION_COUNTER_ID):
        integer old_value = core.UInt(PMICNTR_EL0);
        integer new_value = old_value + increment;
        PMICNTR_EL0       = core.Field(new_value,63,0);
        # The effective value of PMCR_EL0.LP is '1' for the instruction counter
        if core.Bit(old_value,64) != core.Bit(new_value,64):
            PMOVSSET_EL0.F0 = '1';
            PMOVSCLR_EL0.F0 = '1';
array integer PMUEventAccumulator[0..30];  # Accumulates PMU events for a cycle
array boolean PMULastThresholdValue[0..30];# A record of the threshold result for each
# core.HaveStatisticalProfilingv1p1()
# ==============================
# Returns True if the SPEv1p1 extension is implemented, and False otherwise.
boolean core.HaveStatisticalProfilingv1p1()
    return core.IsFeatureImplemented(FEAT_SPEv1p1);
# core.HaveStatisticalProfilingv1p4()
# ==============================
# Returns True if the SPEv1p4 extension is implemented, and False otherwise.
boolean core.HaveStatisticalProfilingv1p4()
    return core.IsFeatureImplemented(FEAT_SPEv1p4);
# core.HaveStatisticalProfilingv1p2()
# ==============================
# Returns True if the SPEv1p2 extension is implemented, and False otherwise.
boolean core.HaveStatisticalProfilingv1p2()
    return core.IsFeatureImplemented(FEAT_SPEv1p2);
# OpType
# ======
# Types of operation filtered by core.SPECollectRecord().
enumeration OpType {
    OpType_Load,        # Any memory-read operation other than atomics, compare-and-swap, and swap
    OpType_Store,       # Any memory-write operation, including atomics without return
    OpType_LoadAtomic,  # Atomics with return, compare-and-swap and swap
    OpType_Branch,      # Software write to the PC
    OpType_Other        # Any other class of operation
};
# core.SPEBufferFilled()
# =================
# Deal with a full buffer event.
core.SPEBufferFilled()
    if core.IsZero(PMBSR_EL1.S):
        PMBSR_EL1.S = '1';                          # Assert PMBIRQ
        PMBSR_EL1.EC = '000000';                    # Other buffer management event
        PMBSR_EL1.MSS = core.ZeroExtend('000001', 16);   # Set buffer full event
    core.PMUEvent(PMU_EVENT_SAMPLE_WRAP);
# core.SPEBufferIsFull()
# =================
# Return true if another full size sample record would not fit in the
# profiling buffer.
boolean core.SPEBufferIsFull()
    integer write_pointer_limit = core.UInt(PMBLIMITR_EL1.LIMIT:core.Zeros(12));
    integer current_write_pointer = core.UInt(PMBPTR_EL1);
    integer record_max_size = 1<<core.UInt(PMSIDR_EL1.MaxSize);
    return current_write_pointer > (write_pointer_limit - record_max_size);
# core.HaveSVE()
# =========
boolean core.HaveSVE()
    return core.IsFeatureImplemented(FEAT_SVE);
# core.HaveStatisticalProfilingFDS()
# =============================
# Returns True if the SPE_FDS extension is implemented, and False otherwise.
boolean core.HaveStatisticalProfilingFDS()
    return core.IsFeatureImplemented(FEAT_SPE_FDS);
# core.HaveStatisticalProfiling()
# ==========================
# Returns True if Statistical Profiling Extension is implemented,
# and False otherwise.
boolean core.HaveStatisticalProfiling()
    return core.IsFeatureImplemented(FEAT_SPE);
# Constraint
# ==========
# List of Constrained Unpredictable behaviors.
enumeration Constraint    {# General
                           Constraint_NONE,              # Instruction executes with
                                                         # no change or side-effect
                                                         # to its described behavior
                           Constraint_UNKNOWN,           # Destination register
                                                         # has UNKNOWN value
                           Constraint_UNDEF,             # Instruction is raise Exception('UNDEFINED')
                           Constraint_UNDEFEL0,          # Instruction is raise Exception('UNDEFINED') at EL0 only
                           Constraint_NOP,               # Instruction executes as NOP
                           Constraint_True,
                           Constraint_False,
                           Constraint_DISABLED,
                           Constraint_UNCOND,            # Instruction executes unconditionally
                           Constraint_COND,              # Instruction executes conditionally
                           Constraint_ADDITIONAL_DECODE, # Instruction executes
                                                         # with additional decode
                           # Load-store
                           Constraint_WBSUPPRESS,
                           Constraint_FAULT,
                           Constraint_LIMITED_ATOMICITY, # Accesses are not
                                                         # single-copy atomic
                                                         # above the byte level
                           Constraint_NVNV1_00,
                           Constraint_NVNV1_01,
                           Constraint_NVNV1_11,
                           Constraint_EL1TIMESTAMP,      # Constrain to Virtual Timestamp
                           Constraint_EL2TIMESTAMP,      # Constrain to Virtual Timestamp
                           Constraint_OSH,               # Constrain to Outer Shareable
                           Constraint_ISH,               # Constrain to Inner Shareable
                           Constraint_NSH,               # Constrain to Nonshareable
                           Constraint_NC,                # Constrain to Noncacheable
                           Constraint_WT,                # Constrain to Writethrough
                           Constraint_WB,                # Constrain to Writeback
                           # IPA too large
                           Constraint_FORCE, Constraint_FORCENOSLCHECK,
                           # An unallocated System register value maps onto an allocated value
                           Constraint_MAPTOALLOCATED,
                           # PMSCR_PCT reserved values select Virtual timestamp
                           Constraint_PMSCR_PCT_VIRT
};
# core.ConstrainUnpredictableBits()
# ============================
# This is a variant of ConstrainUnpredictable for when the result can be Constraint_UNKNOWN.
# If the result is Constraint_UNKNOWN then the function also returns UNKNOWN value, but that
# value is always an allocated value; that is, one for which the behavior is not itself
# CONSTRAINED.
(Constraint,core.bits(width)) core.ConstrainUnpredictableBits(Unpredictable which, integer width);
# core.ProfilingBufferOwner()
# ======================
(SecurityState, core.bits(2)) core.ProfilingBufferOwner()
    SecurityState owning_ss;
    if core.HaveEL(EL3):
        state_bits = 0;
        if core.HaveRME():
            state_bits = MDCR_EL3.<NSPBE,NSPB>;
            if (state_bits IN {'10x'} or
                (not core.HaveSecureEL2Ext() and state_bits IN {'00x'})) then
                # Reserved value
                (-, state_bits) = core.ConstrainUnpredictableBits(Unpredictable_RESERVEDNSxB, 3);
        else:
            state_bits = '0' : MDCR_EL3.NSPB;
        case state_bits of
            when '00x' owning_ss = SS_Secure;
            when '01x' owning_ss = SS_NonSecure;
            when '11x' owning_ss = SS_Realm;
    else:
        owning_ss = SS_Secure if core.SecureOnlyImplementation() else SS_NonSecure;
    owning_el = 0;
    if core.HaveEL(EL2) and (owning_ss != SS_Secure or core.IsSecureEL2Enabled()):
        owning_el = EL2 if MDCR_EL2.E2PB == '00' else EL1;
    else:
        owning_el = EL1;
    return (owning_ss, owning_el);
# core.ProfilingBufferEnabled()
# ========================
boolean core.ProfilingBufferEnabled()
    if not core.HaveStatisticalProfiling():
         return False;
    (owning_ss, owning_el) = core.ProfilingBufferOwner();
    state_bits = 0;
    if core.HaveRME():
        state_bits = SCR_EL3.NSE : core.EffectiveSCR_EL3_NS();
    else:
        state_bits = '0' : SCR_EL3.NS;
    state_match = False;
    case owning_ss of
        when SS_Secure    state_match = state_bits == '00';
        when SS_NonSecure state_match = state_bits == '01';
        when SS_Realm     state_match = state_bits == '11';
    return (not core.ELUsingAArch32(owning_el) and state_match and
            PMBLIMITR_EL1.E == '1' and PMBSR_EL1.S == '0');
# core.StatisticalProfilingEnabled()
# =============================
# Return True if Statistical Profiling is Enabled in the current EL, False otherwise.
boolean core.StatisticalProfilingEnabled()
    return core.StatisticalProfilingEnabled(core.APSR.EL);
# core.StatisticalProfilingEnabled()
# =============================
# Return True if Statistical Profiling is Enabled in the specified EL, False otherwise.
boolean core.StatisticalProfilingEnabled(core.bits(2) el)
    if not core.HaveStatisticalProfiling() or core.UsingAArch32() or not core.ProfilingBufferEnabled():
        return False;
    tge_set = core.EL2Enabled() and HCR_EL2.TGE == '1';
    (owning_ss, owning_el) = core.ProfilingBufferOwner();
    if (core.UInt(owning_el) <  core.UInt(el) or (tge_set and owning_el == EL1) or
            owning_ss != core.SecurityStateAtEL(el))  then
        return False;
    bit spe_bit;
    case el of
        when EL3  core.Unreachable();
        when EL2  spe_bit = PMSCR_EL2.E2SPE;
        when EL1  spe_bit = PMSCR_EL1.E1SPE;
        when EL0  spe_bit = (PMSCR_EL2.E0HSPE if tge_set else PMSCR_EL1.E0SPE);
    return spe_bit == '1';
# core.SPECollectRecord()
# ==================
# Returns True if the sampled class of instructions or operations, as
# determined by PMSFCR_EL1, are recorded and False otherwise.
boolean core.SPECollectRecord(core.bits(64) events, integer total_latency, OpType optype)
    assert core.StatisticalProfilingEnabled();
    core.bits(64) mask = core.Field(0xAA,63,0);                             # Bits [7,5,3,1]
    e = 0;
    m = 0;
    if core.HaveSVE():
         mask = core.SetField(mask,18,17,'11');                   # Predicate flags
    if core.HaveTME():
         mask = core.SetBit(mask,16,'1')
    if core.HaveStatisticalProfilingv1p1():
         mask = core.SetBit(mask,11,'1')  # Alignment Flag
    if core.HaveStatisticalProfilingv1p2():
         mask = core.SetBit(mask,6,'1')   # Not taken flag
    if core.HaveStatisticalProfilingv1p4():
        mask<10:8,4,2> = '11111';
    else:
        impdef_mask = 0;
        impdef_mask = core.bits(5) IMPLEMENTATION_DEFINED "SPE mask 10:8,4,2";
        mask<10:8,4,2> = impdef_mask;
    mask = core.SetField(mask,63,48,core.bits(16) IMPLEMENTATION_DEFINED "SPE mask 63:48");
    mask = core.SetField(mask,31,24,core.bits(8) IMPLEMENTATION_DEFINED "SPE mask 31:24");
    mask = core.SetField(mask,15,12,core.bits(4) IMPLEMENTATION_DEFINED "SPE mask 15:12");
    e = events & mask;
    boolean is_rejected_nevent = False;
    is_nevt = False;
    # Filtering by inverse event
    if core.HaveStatisticalProfilingv1p2():
        m = PMSNEVFR_EL1 & mask;
        is_nevt = core.IsZero(e & m);
        if PMSFCR_EL1.FnE == '1':
            # Inverse filtering by event is enabled
            if not core.IsZero(m):
                # Not raise Exception('UNPREDICTABLE') case
                is_rejected_nevent = not is_nevt;
            else:
                is_rejected_nevent = core.ConstrainUnpredictableBool(Unpredictable_BADPMSFCR);
    else:
        is_nevt = True; # not implemented
    boolean is_rejected_event = False;
    # Filtering by event
    m = PMSEVFR_EL1 & mask;
    boolean is_evt = core.IsZero(core.NOT(e) & m);
    if PMSFCR_EL1.FE == '1':
        # Filtering by event is enabled
        if not core.IsZero(m):
            # Not raise Exception('UNPREDICTABLE') case
            is_rejected_event = not is_evt;
        else:
            is_rejected_event = core.ConstrainUnpredictableBool(Unpredictable_BADPMSFCR);
    if (core.HaveStatisticalProfilingv1p2() and PMSFCR_EL1.<FnE,FE> == '11' and
            not core.IsZero(PMSEVFR_EL1 & PMSNEVFR_EL1 & mask)) then
        # raise Exception('UNPREDICTABLE') case due to combination of filter and inverse filter
        is_rejected_nevent = core.ConstrainUnpredictableBool(Unpredictable_BADPMSFCR);
        is_rejected_event = core.ConstrainUnpredictableBool(Unpredictable_BADPMSFCR);
    if is_evt and is_nevt:
        core.PMUEvent(PMU_EVENT_SAMPLE_FEED_EVENT);
    boolean is_op_br = False;
    boolean is_op_ld = False;
    boolean is_op_st = False;
    is_op_br = (optype == OpType_Branch);
    is_op_ld = (optype IN {OpType_Load, OpType_LoadAtomic});
    is_op_st = (optype IN {OpType_Store, OpType_LoadAtomic});
    if is_op_br:
         core.PMUEvent(PMU_EVENT_SAMPLE_FEED_BR);
    if is_op_ld:
         core.PMUEvent(PMU_EVENT_SAMPLE_FEED_LD);
    if is_op_st:
         core.PMUEvent(PMU_EVENT_SAMPLE_FEED_ST);
    boolean is_op = ((is_op_br and PMSFCR_EL1.B == '1') or
                    (is_op_ld and PMSFCR_EL1.LD == '1') or
                    (is_op_st and PMSFCR_EL1.ST == '1'));
    if is_op:
         core.PMUEvent(PMU_EVENT_SAMPLE_FEED_OP);
    # Filter by type1
    boolean is_rejected_type = False;
    if PMSFCR_EL1.FT == '1':
        # Filtering by type1 is enabled
        if not core.IsZero(PMSFCR_EL1.<B, LD, ST>):
            # Not an raise Exception('UNPREDICTABLE') case
            is_rejected_type = not is_op;
        else:
            is_rejected_type = core.ConstrainUnpredictableBool(Unpredictable_BADPMSFCR);
    # Filter by latency
    boolean is_rejected_latency = False;
    boolean is_lat = (total_latency < core.UInt(PMSLATFR_EL1.MINLAT));
    if is_lat:
         core.PMUEvent(PMU_EVENT_SAMPLE_FEED_LAT);
    if PMSFCR_EL1.FL == '1':
        # Filtering by latency is enabled
        if not core.IsZero(PMSLATFR_EL1.MINLAT):
            # Not an raise Exception('UNPREDICTABLE') case
            is_rejected_latency = not is_lat;
        else:
            is_rejected_latency = core.ConstrainUnpredictableBool(Unpredictable_BADPMSFCR);
    is_rejected_data_source = False;
    # Filtering by Data Source
    if (core.HaveStatisticalProfilingFDS() and PMSFCR_EL1.FDS == '1' and
            is_op_ld and SPESampleDataSourceValid) then
        core.bits(16) data_source = SPESampleDataSource;
        integer index = core.UInt(core.Field(data_source,5,0));
        is_rejected_data_source = PMSDSFR_EL1<index> == '0';
    else:
        is_rejected_data_source = False;
    return_value = False;
    return_value = not (is_rejected_nevent or is_rejected_event or
                     is_rejected_type or is_rejected_latency);
    if return_value:
        core.PMUEvent(PMU_EVENT_SAMPLE_FILTRATE);
    return return_value;
constant integer SPEMaxRecordSize = 64;
constant integer SPEMaxAddrs = 32;
constant integer SPEMaxCounters = 32;
SPERecordSize = 0;
# core.SPEResetSampleStorage()
# =======================
# Reset all variables inside sample storage.
core.SPEResetSampleStorage()
    # Context values
    SPESampleContextEL1 = core.Zeros(32);
    SPESampleContextEL1Valid = False;
    SPESampleContextEL2 = core.Zeros(32);
    SPESampleContextEL2Valid = False;
    # Counter values
    for i = 0 to (SPEMaxCounters - 1)
        SPESampleCounter[i] = 0;
        SPESampleCounterValid[i] = False;
        SPESampleCounterPending[i] = False;
    # Address values
    for i = 0 to (SPEMaxAddrs - 1)
        SPESampleAddressValid[i] = False;
        SPESampleAddress[i] = core.Zeros(64);
    # Data source values
    SPESampleDataSource = core.Zeros(16);
    SPESampleDataSourceValid = False;
    # Operation values
    SPESampleClass = core.Zeros(2);
    SPESampleSubclass = core.Zeros(8);
    SPESampleSubclassValid = False;
    # Timestamp values
    SPESampleTimestamp = core.Zeros(64);
    SPESampleTimestampValid = False;
    # Event values
    SPESampleEvents = core.SetField(SPESampleEvents,63,48,core.bits(16) IMPLEMENTATION_DEFINED "SPE EVENTS 63_48");
    SPESampleEvents = core.SetField(SPESampleEvents,47,32,core.Zeros(16));
    SPESampleEvents = core.SetField(SPESampleEvents,31,24,core.bits(8) IMPLEMENTATION_DEFINED "SPE EVENTS 31_24");
    SPESampleEvents = core.SetField(SPESampleEvents,23,16,core.Zeros(8));
    SPESampleEvents = core.SetField(SPESampleEvents,15,12,core.bits(4) IMPLEMENTATION_DEFINED "SPE EVENTS 15_12");
    SPESampleEvents = core.SetField(SPESampleEvents,11,0,core.Zeros(12));
    SPESampleInstIsNV2 = False;
array [0..SPEMaxRecordSize-1] of SPERecordData = 0;
# core.SPEAddByteToRecord()
# ====================
# Add one byte to a record and increase size property appropriately.
core.SPEAddByteToRecord(core.bits(8) b)
    assert SPERecordSize < SPEMaxRecordSize;
    SPERecordData[SPERecordSize] = b;
    SPERecordSize = SPERecordSize + 1;
# core.SPEAddPacketToRecord()
# ======================
# Add passed header and payload data to the record.
# Payload must be a multiple of 8.
core.SPEAddPacketToRecord(core.bits(2) header_hi, core.bits(4) header_lo,
                        core.bits(N) payload)
    assert N MOD 8 == 0;
    sz = 0;
    case N of
        when 8 sz = '00';
        when 16 sz = '01';
        when 32 sz = '10';
        when 64 sz = '11';
        otherwise core.Unreachable();
    core.bits(8) header = header_hi:sz:header_lo;
    core.SPEAddByteToRecord(header);
    for i = 0 to (N DIV 8)-1
        core.SPEAddByteToRecord(payload<i*8+7:i*8>);
# core.SPEEmptyRecord()
# ================
# Reset record data.
core.SPEEmptyRecord()
    SPERecordSize = 0;
    for i = 0 to (SPEMaxRecordSize - 1)
        SPERecordData[i] = core.Zeros(8);
# core.SPEGetDataSourcePayloadSize()
# =============================
# Returns the size of the Data Source payload in bytes.
integer core.SPEGetDataSourcePayloadSize()
    return integer IMPLEMENTATION_DEFINED "SPE Data Source packet payload size";
# core.SPEGetEventsPayloadSize()
# =========================
# Returns the size in bytes of the Events packet payload as an integer.
integer core.SPEGetEventsPayloadSize()
    integer size = integer IMPLEMENTATION_DEFINED "SPE Events packet payload size";
    return size;
# AccessType
# ==========
enumeration AccessType {
    AccessType_IFETCH,  # Instruction FETCH
    AccessType_GPR,     # Software load/store to a General Purpose Register
    AccessType_ASIMD,   # Software ASIMD extension load/store instructions
    AccessType_SVE,     # Software SVE load/store instructions
    AccessType_SME,     # Software SME load/store instructions
    AccessType_IC,      # Sysop IC
    AccessType_DC,      # Sysop DC (not DC {Z,G,GZ}VA)
    AccessType_DCZero,  # Sysop DC {Z,G,GZ}VA
    AccessType_AT,      # Sysop AT
    AccessType_NV2,     # NV2 memory redirected access
    AccessType_SPE,     # Statistical Profiling buffer access
    AccessType_GCS,     # Guarded Control Stack access
    AccessType_TRBE,    # Trace Buffer access
    AccessType_GPTW,    # Granule Protection Table Walk
    AccessType_TTW      # Translation Table Walk
};
# MemAtomicOp
# ===========
# Atomic data processing instruction types.
enumeration MemAtomicOp {
    MemAtomicOp_GCSSS1,
    MemAtomicOp_ADD,
    MemAtomicOp_BIC,
    MemAtomicOp_^,
    MemAtomicOp_ORR,
    MemAtomicOp_SMAX,
    MemAtomicOp_SMIN,
    MemAtomicOp_UMAX,
    MemAtomicOp_UMIN,
    MemAtomicOp_SWP,
    MemAtomicOp_CAS
};
enumeration CacheOp {
    CacheOp_Clean,
    CacheOp_Invalidate,
    CacheOp_CleanInvalidate
};
enumeration CacheOpScope {
    CacheOpScope_SetWay,
    CacheOpScope_PoU,
    CacheOpScope_PoC,
    CacheOpScope_PoE,
    CacheOpScope_PoP,
    CacheOpScope_PoDP,
    CacheOpScope_ALLU,
    CacheOpScope_ALLUIS
};
enumeration CacheType {
    CacheType_Data,
    CacheType_Tag,
    CacheType_Data_Tag,
    CacheType_Instruction
};
enumeration CachePASpace {
    CPAS_NonSecure,
    CPAS_Any,               # Applicable only for DC *SW / IC IALLU* in Root state:
                            # match entries from any PA Space
    CPAS_RealmNonSecure,    # Applicable only for DC *SW / IC IALLU* in Realm state:
                            # match entries from Realm or Non-Secure PAS
    CPAS_Realm,
    CPAS_Root,
    CPAS_SecureNonSecure,   # Applicable only for DC *SW / IC IALLU* in Secure state:
                            # match entries from Secure or Non-Secure PAS
    CPAS_Secure
};
# MPAM Types
# ==========
type PARTIDtype = core.bits(16);
type PMGtype = core.bits(8);
enumeration PARTIDspaceType {
    PIdSpace_Secure,
    PIdSpace_Root,
    PIdSpace_Realm,
    PIdSpace_NonSecure
};
type MPAMinfo is (
     PARTIDspaceType mpam_sp,
     PARTIDtype partid,
     PMGtype pmg
)
# VARange
# =======
# Virtual address ranges
enumeration VARange {
    VARange_LOWER,
    VARange_UPPER
};
# AccessDescriptor
# ================
# Memory access or translation invocation details that steer architectural behavior
type AccessDescriptor is (
    AccessType acctype,
    core.bits(2) el,             # Acting EL for the access
    SecurityState ss,       # Acting Security State for the access
    boolean acqsc,          # Acquire with Sequential Consistency
    boolean acqpc,          # FEAT_LRCPC: Acquire with Processor Consistency
    boolean relsc,          # Release with Sequential Consistency
    boolean limitedordered, # FEAT_LOR: Acquire/Release with limited ordering
    boolean exclusive,      # Access has Exclusive semantics
    boolean atomicop,       # FEAT_LSE: Atomic read-modify-write access
    MemAtomicOp modop,      # FEAT_LSE: The modification operation in the 'atomicop' access
    boolean nontemporal,    # Hints the access is non-temporal
    boolean read,           # Read from memory or only require read permissions
    boolean write,          # Write to memory or only require write permissions
    CacheOp cacheop,        # DC/IC: Cache operation
    CacheOpScope opscope,   # DC/IC: Scope of cache operation
    CacheType cachetype,    # DC/IC: Type of target cache
    boolean pan,            # FEAT_PAN: The access is subject to core.APSR.PAN
    boolean transactional,  # FEAT_TME: Access is part of a transaction
    boolean nonfault,       # SVE: Non-faulting load
    boolean firstfault,     # SVE: First-fault load
    boolean first,          # SVE: First-fault load for the first active element
    boolean contiguous,     # SVE: Contiguous load/store not gather load/scatter store
    boolean streamingsve,   # SME: Access made by PE while in streaming SVE mode
    boolean ls64,           # FEAT_LS64: Accesses by accelerator support loads/stores
    boolean mops,           # FEAT_MOPS: Memory operation (CPY/SET) accesses
    boolean rcw,            # FEAT_THE: Read-Check-Write access
    boolean rcws,           # FEAT_THE: Read-Check-Write Software access
    boolean toplevel,       # FEAT_THE: Translation table walk access for TTB address
    VARange varange,        # FEAT_THE: The corresponding TTBR supplying the TTB
    boolean a32lsmd,        # A32 Load/Store Multiple Data access
    boolean tagchecked,     # FEAT_MTE2: Access is tag checked
    boolean tagaccess,      # FEAT_MTE: Access targets the tag bits
    MPAMinfo mpam           # FEAT_MPAM: MPAM information
)
# ErrorState
# ==========
# The allowed error states that can be returned by memory and used by the PE.
enumeration ErrorState {ErrorState_UC,            # Uncontainable
                        ErrorState_UEU,           # Unrecoverable state
                        ErrorState_UEO,           # Restartable state
                        ErrorState_UER,           # Recoverable state
                        ErrorState_CE,            # Corrected
                        ErrorState_Uncategorized,
                        ErrorState_IMPDEF};
# Fault
# =====
# Fault types.
enumeration Fault {Fault_None,
                   Fault_AccessFlag,
                   Fault_Alignment,
                   Fault_Background,
                   Fault_Domain,
                   Fault_Permission,
                   Fault_Translation,
                   Fault_AddressSize,
                   Fault_SyncExternal,
                   Fault_SyncExternalOnWalk,
                   Fault_SyncParity,
                   Fault_SyncParityOnWalk,
                   Fault_GPCFOnWalk,
                   Fault_GPCFOnOutput,
                   Fault_AsyncParity,
                   Fault_AsyncExternal,
                   Fault_TagCheck,
                   Fault_Debug,
                   Fault_TLBConflict,
                   Fault_BranchTarget,
                   Fault_HWUpdateAccessFlag,
                   Fault_Lockdown,
                   Fault_Exclusive,
                   Fault_ICacheMaint};
# GPCF
# ====
# Possible Granule Protection Check Fault reasons
enumeration GPCF {
    GPCF_None,        # No fault
    GPCF_AddressSize, # GPT address size fault
    GPCF_Walk,        # GPT walk fault
    GPCF_EABT,        # Synchronous External abort on GPT fetch
    GPCF_Fail         # Granule protection fault
};
# GPCFRecord
# ==========
# Full details of a Granule Protection Check Fault
type GPCFRecord is (
    GPCF    gpf,
    integer level
)
# FaultRecord
# ===========
# Fields that relate only to Faults.
type FaultRecord is (
    Fault            statuscode,  # Fault Status
    AccessDescriptor access,      # Details of the faulting access
    FullAddress      ipaddress,   # Intermediate physical address
    GPCFRecord       gpcf,        # Granule Protection Check Fault record
    FullAddress      paddress,    # Physical address
    boolean          gpcfs2walk,  # GPC for a stage 2 translation table walk
    boolean          s2fs1walk,   # Is on a Stage 1 translation table walk
    boolean          write,       # True for a write, False for a read
    boolean          s1tagnotdata,# True for a fault due to tag not accessible at stage 1.
    boolean          tagaccess,   # True for a fault due to NoTagAccess permission.
    integer          level,       # For translation, access flag and Permission faults
    bit              extflag,     # IMPLEMENTATION DEFINED syndrome for External aborts
    boolean          secondstage, # Is a Stage 2 abort
    boolean          assuredonly, # Stage 2 Permission fault due to AssuredOnly attribute
    boolean          toplevel,    # Stage 2 Permission fault due to TopLevel
    boolean          overlay,     # Fault due to overlay permissions
    boolean          dirtybit,    # Fault due to dirty state
    core.bits(4)          domain,      # Domain number, AArch32 only
    ErrorState       merrorstate, # Incoming error state from memory
    core.bits(4)          debugmoe     # Debug method of entry, from AArch32 only
)
# DeviceType
# ==========
# Extended memory types for Device memory.
enumeration DeviceType {DeviceType_GRE, DeviceType_nGRE, DeviceType_nGnRE, DeviceType_nGnRnE};
# MemAttrHints
# ============
# Attributes and hints for Normal memory.
type MemAttrHints is (
    core.bits(2) attrs,  # See MemAttr_*, Cacheability attributes
    core.bits(2) hints,  # See MemHint_*, Allocation hints
    boolean transient
)
# Memory Tag type1
# ===============
enumeration MemTagType {
    MemTag_Untagged,
    MemTag_AllocationTagged,
    MemTag_CanonicallyTagged
};
# MemType
# =======
# Basic memory types.
enumeration MemType {MemType_Normal, MemType_Device};
# Shareability
# ============
enumeration Shareability {
    Shareability_NSH,
    Shareability_ISH,
    Shareability_OSH
};
# MemoryAttributes
# ================
# Memory attributes descriptor
type MemoryAttributes is (
    MemType      memtype,
    DeviceType   device,       # For Device memory types
    MemAttrHints inner,        # Inner hints and attributes
    MemAttrHints outer,        # Outer hints and attributes
    Shareability shareability, # Shareability attribute
    MemTagType   tags,         # MTE tag type1 for this memory.
    boolean      notagaccess,  # Allocation Tag access permission
    bit          xs            # XS attribute
)
constant integer FINAL_LEVEL = 3;
# AddressDescriptor
# =================
# Descriptor used to access the underlying memory array.
type AddressDescriptor is (
    FaultRecord      fault,      # fault.statuscode indicates whether the address is valid
    MemoryAttributes memattrs,
    FullAddress      paddress,
    boolean          s1assured,  # Stage 1 Assured Translation Property
    boolean          s2fs1mro,   # Stage 2 MRO permission for Satge 1
    core.bits(16)         mecid,      # FEAT_MEC: Memory Encryption Context ID
    core.bits(64)         vaddress
)
# core.MPAMisEnabled()
# ===============
# Returns True if MPAMisEnabled.
boolean core.MPAMisEnabled()
    el = core.HighestEL();
    case el of
        when EL3 return MPAM3_EL3.MPAMEN == '1';
        when EL2 return MPAM2_EL2.MPAMEN == '1';
        when EL1 return MPAM1_EL1.MPAMEN == '1';
# core.UsePrimarySpaceEL10()
# =====================
# Checks whether Primary space is configured in the
# MPAM3_EL3 and MPAM2_EL2 ALTSP control bits that affect
# MPAM ALTSP use at EL1 and EL0.
boolean core.UsePrimarySpaceEL10()
    if MPAM3_EL3.ALTSP_HEN == '0':
        return MPAM3_EL3.ALTSP_HFC == '0';
    return not core.MPAMisEnabled() or not core.EL2Enabled() or MPAM2_EL2.ALTSP_HFC == '0';
# core.UsePrimarySpaceEL2()
# ====================
# Checks whether Primary space is configured in the
# MPAM3_EL3 and MPAM2_EL2 ALTSP control bits that affect
# MPAM ALTSP use at EL2.
boolean core.UsePrimarySpaceEL2()
    if MPAM3_EL3.ALTSP_HEN == '0':
        return MPAM3_EL3.ALTSP_HFC == '0';
    return not core.MPAMisEnabled() or MPAM2_EL2.ALTSP_EL2 == '0';
# core.AltPIdRealm()
# =============
# Compute PARTID space as either the primary PARTID space or
# alternative PARTID space in the Realm Security state.
# Helper for AltPARTIDspace.
PARTIDspaceType core.AltPIdRealm(core.bits(2) el, PARTIDspaceType primaryPIdSpace)
    PARTIDspaceType PIdSpace = primaryPIdSpace;
    case el of
        when EL0
            if core.ELIsInHost(EL0):
                if not core.UsePrimarySpaceEL2():
                    PIdSpace = PIdSpace_NonSecure;
            elsif not core.UsePrimarySpaceEL10():
                PIdSpace = PIdSpace_NonSecure;
        when EL1
            if not core.UsePrimarySpaceEL10():
                PIdSpace = PIdSpace_NonSecure;
        when EL2
            if not core.UsePrimarySpaceEL2():
                PIdSpace = PIdSpace_NonSecure;
        otherwise
            core.Unreachable();
    return PIdSpace;
# core.AltPIdSecure()
# ==============
# Compute PARTID space as either the primary PARTID space or
# alternative PARTID space in the Secure Security state.
# Helper for AltPARTIDspace.
PARTIDspaceType core.AltPIdSecure(core.bits(2) el, PARTIDspaceType primaryPIdSpace)
    PARTIDspaceType PIdSpace = primaryPIdSpace;
    boolean el2en = core.EL2Enabled();
    case el of
        when EL0
            if el2en:
                if core.ELIsInHost(EL0):
                    if not core.UsePrimarySpaceEL2():
                        PIdSpace = PIdSpace_NonSecure;
                elsif not core.UsePrimarySpaceEL10():
                    PIdSpace = PIdSpace_NonSecure;
            elsif MPAM3_EL3.ALTSP_HEN == '0' and MPAM3_EL3.ALTSP_HFC == '1':
                PIdSpace = PIdSpace_NonSecure;
        when EL1
            if el2en:
                if not core.UsePrimarySpaceEL10():
                    PIdSpace = PIdSpace_NonSecure;
            elsif MPAM3_EL3.ALTSP_HEN == '0' and MPAM3_EL3.ALTSP_HFC == '1':
                PIdSpace = PIdSpace_NonSecure;
        when EL2
            if not core.UsePrimarySpaceEL2():
                PIdSpace = PIdSpace_NonSecure;
        otherwise
            core.Unreachable();
    return PIdSpace;
# core.AltPARTIDspace()
# ================
# From the Security state, EL and ALTSP configuration, determine
# whether to primary space or the alt space is selected and which
# PARTID space is the alternative space. Return that alternative
# PARTID space if selected or the primary space if not.
PARTIDspaceType core.AltPARTIDspace(core.bits(2) el, SecurityState security,
                                PARTIDspaceType primaryPIdSpace)
    case security of
        when SS_NonSecure
            assert el != EL3;
            return primaryPIdSpace; # there is no ALTSP for Non_secure
        when SS_Secure
            assert el != EL3;
            if primaryPIdSpace == PIdSpace_NonSecure:
                return primaryPIdSpace;
            return core.AltPIdSecure(el, primaryPIdSpace);
        when SS_Root
            assert el == EL3;
            if MPAM3_EL3.ALTSP_EL3 == '1':
                if MPAM3_EL3.RT_ALTSP_NS == '1':
                    return PIdSpace_NonSecure;
                else:
                    return PIdSpace_Secure;
            else:
                return primaryPIdSpace;
        when SS_Realm
            assert el != EL3;
            return core.AltPIdRealm(el, primaryPIdSpace);
        otherwise
            core.Unreachable();
constant PARTIDtype DefaultPARTID = core.Field(0,15,0);
constant PMGtype    DefaultPMG = core.Field(0,7,0);
# core.DefaultMPAMinfo()
# =================
# Returns default MPAM info.  The partidspace argument sets
# the PARTID space of the default MPAM information returned.
MPAMinfo core.DefaultMPAMinfo(PARTIDspaceType partidspace)
    MPAMinfo DefaultInfo;
    DefaultInfo.mpam_sp = partidspace;
    DefaultInfo.partid  = DefaultPARTID;
    DefaultInfo.pmg     = DefaultPMG;
    return DefaultInfo;
# core.HaveMPAMv0p1Ext()
# =================
# Returns True if MPAMv0p1 is implemented, and False otherwise.
boolean core.HaveMPAMv0p1Ext()
    return core.IsFeatureImplemented(FEAT_MPAMv0p1);
# core.HaveMPAMv1p1Ext()
# =================
# Returns True if MPAMv1p1 is implemented, and False otherwise.
boolean core.HaveMPAMv1p1Ext()
    return core.IsFeatureImplemented(FEAT_MPAMv1p1);
# core.HaveSME()
# =========
# Returns True if the SME extension is implemented, False otherwise.
boolean core.HaveSME()
    return core.IsFeatureImplemented(FEAT_SME);
# core.PARTIDspaceFromSS()
# ===================
# Returns the primary PARTID space from the Security State.
PARTIDspaceType core.PARTIDspaceFromSS(SecurityState security)
    case security of
        when SS_NonSecure
            return PIdSpace_NonSecure;
        when SS_Root
            return PIdSpace_Root;
        when SS_Realm
            return PIdSpace_Realm;
        when SS_Secure
            return PIdSpace_Secure;
        otherwise
            core.Unreachable();
# core.mapvpmw()
# =========
# Map a virtual PARTID into a physical PARTID using
# the MPAMVPMn_EL2 registers.
# vpartid is now assumed in-range and valid (checked by caller)
# returns physical PARTID from mapping entry.
PARTIDtype core.mapvpmw(integer vpartid)
    vpmw = 0;
    integer  wd = vpartid DIV 4;
    case wd of
        when 0 vpmw = MPAMVPM0_EL2;
        when 1 vpmw = MPAMVPM1_EL2;
        when 2 vpmw = MPAMVPM2_EL2;
        when 3 vpmw = MPAMVPM3_EL2;
        when 4 vpmw = MPAMVPM4_EL2;
        when 5 vpmw = MPAMVPM5_EL2;
        when 6 vpmw = MPAMVPM6_EL2;
        when 7 vpmw = MPAMVPM7_EL2;
        otherwise vpmw = core.Zeros(64);
    # vpme_lsb selects LSB of field within register
    integer vpme_lsb = (vpartid MOD 4) * 16;
    return vpmw<vpme_lsb +: 16>;
# core.MAP_vPARTID()
# =============
# Performs conversion of virtual PARTID into physical PARTID
# Contains all of the error checking and implementation
# choices for the conversion.
(PARTIDtype, boolean) core.MAP_vPARTID(PARTIDtype vpartid)
    # should not ever be called if EL2 is not implemented
    # or is implemented but not enabled in the current
    # security state.
    PARTIDtype ret;
    err = False;
    integer virt    = core.UInt(vpartid);
    integer vpmrmax = core.UInt(MPAMIDR_EL1.VPMR_MAX);
    # vpartid_max is largest vpartid supported
    integer vpartid_max = (vpmrmax << 2) + 3;
    # One of many ways to reduce vpartid to value less than vpartid_max.
    if core.UInt(vpartid) > vpartid_max:
        virt = virt MOD (vpartid_max+1);
    # Check for valid mapping entry.
    if MPAMVPMV_EL2<virt> == '1':
        # vpartid has a valid mapping so access the map.
        ret = core.mapvpmw(virt);
        err = False;
    # Is the default virtual PARTID valid?
    elsif core.Bit(MPAMVPMV_EL2,0) == '1':
        # Yes, so use default mapping for vpartid == 0.
        ret = MPAMVPM0_EL2<0 +: 16>;
        err = False;
    # Neither is valid so use default physical PARTID.
    else:
        ret = DefaultPARTID;
        err = True;
    # Check that the physical PARTID is in-range.
    # This physical PARTID came from a virtual mapping entry.
    integer partid_max = core.UInt(MPAMIDR_EL1.PARTID_MAX);
    if core.UInt(ret) > partid_max:
        # Out of range, so return default physical PARTID
        ret = DefaultPARTID;
        err = True;
    return (ret, err);
# core.MPAMisVirtual()
# ===============
# Returns True if MPAM is configured to be virtual at EL.
boolean core.MPAMisVirtual(core.bits(2) el)
    return (MPAMIDR_EL1.HAS_HCR == '1' and core.EL2Enabled() and
            ((el == EL0 and MPAMHCR_EL2.EL0_VPMEN == '1' and
               (HCR_EL2.E2H == '0' or HCR_EL2.TGE == '0')) or
             (el == EL1 and MPAMHCR_EL2.EL1_VPMEN == '1')));
# core.getMPAM_PARTID()
# ================
# Returns a PARTID from one of the MPAMn_ELx or MPAMSM_EL1 registers.
# If InSM is True, the MPAMSM_EL1 register is used. Otherwise,
# MPAMn selects the MPAMn_ELx register used.
# If InD is True, selects the PARTID_I field of that
# register.  Otherwise, selects the PARTID_D field.
PARTIDtype core.getMPAM_PARTID(core.bits(2) MPAMn, boolean InD, boolean InSM)
    PARTIDtype partid;
    boolean el2avail = core.EL2Enabled();
    if InSM:
        partid = MPAMSM_EL1.PARTID_D;
        return partid;
    if InD:
        case MPAMn of
            when '11' partid = MPAM3_EL3.PARTID_I;
            when '10' partid = MPAM2_EL2.PARTID_I if el2avail else core.Zeros(16);
            when '01' partid = MPAM1_EL1.PARTID_I;
            when '00' partid = MPAM0_EL1.PARTID_I;
            otherwise partid = PARTIDtype UNKNOWN;
    else:
        case MPAMn of
            when '11' partid = MPAM3_EL3.PARTID_D;
            when '10' partid = MPAM2_EL2.PARTID_D if el2avail else core.Zeros(16);
            when '01' partid = MPAM1_EL1.PARTID_D;
            when '00' partid = MPAM0_EL1.PARTID_D;
            otherwise partid = PARTIDtype UNKNOWN;
    return partid;
# core.genPARTID()
# ===========
# Returns physical PARTID and error boolean for exception level el.
# If InD is True then PARTID is from MPAMel_ELx.PARTID_I and
# otherwise from MPAMel_ELx.PARTID_D.
# If InSM is True then PARTID is from MPAMSM_EL1.PARTID_D.
(PARTIDtype, boolean) core.genPARTID(core.bits(2) el, boolean InD, boolean InSM)
    PARTIDtype partidel = core.getMPAM_PARTID(el, InD, InSM);
    PARTIDtype partid_max = MPAMIDR_EL1.PARTID_MAX;
    if core.UInt(partidel) > core.UInt(partid_max):
        return (DefaultPARTID, True);
    if core.MPAMisVirtual(el):
        return core.MAP_vPARTID(partidel);
    else:
        return (partidel, False);
# core.getMPAM_PMG()
# =============
# Returns a PMG from one of the MPAMn_ELx or MPAMSM_EL1 registers.
# If InSM is True, the MPAMSM_EL1 register is used. Otherwise,
# MPAMn selects the MPAMn_ELx register used.
# If InD is True, selects the PMG_I field of that
# register.  Otherwise, selects the PMG_D field.
PMGtype core.getMPAM_PMG(core.bits(2) MPAMn, boolean InD, boolean InSM)
    PMGtype pmg;
    boolean el2avail = core.EL2Enabled();
    if InSM:
        pmg = MPAMSM_EL1.PMG_D;
        return pmg;
    if InD:
        case MPAMn of
            when '11' pmg = MPAM3_EL3.PMG_I;
            when '10' pmg = MPAM2_EL2.PMG_I if el2avail else core.Zeros(8);
            when '01' pmg = MPAM1_EL1.PMG_I;
            when '00' pmg = MPAM0_EL1.PMG_I;
            otherwise pmg = PMGtype UNKNOWN;
    else:
        case MPAMn of
            when '11' pmg = MPAM3_EL3.PMG_D;
            when '10' pmg = MPAM2_EL2.PMG_D if el2avail else core.Zeros(8);
            when '01' pmg = MPAM1_EL1.PMG_D;
            when '00' pmg = MPAM0_EL1.PMG_D;
            otherwise pmg = PMGtype UNKNOWN;
    return pmg;
# core.genPMG()
# ========
# Returns PMG for exception level el and I- or D-side (InD).
# If PARTID generation (genPARTID) encountered an error, core.genPMG() should be
# called with partid_err as True.
PMGtype core.genPMG(core.bits(2) el, boolean InD, boolean InSM, boolean partid_err)
    integer pmg_max = core.UInt(MPAMIDR_EL1.PMG_MAX);
    # It is CONSTRAINED raise Exception('UNPREDICTABLE') whether partid_err forces PMG to
    # use the default or if it uses the PMG from getMPAM_PMG.
    if partid_err:
        return DefaultPMG;
    PMGtype groupel = core.getMPAM_PMG(el, InD, InSM);
    if core.UInt(groupel) <= pmg_max:
        return groupel;
    return DefaultPMG;
# core.genMPAM()
# =========
# Returns MPAMinfo for exception level el.
# If InD is True returns MPAM information using PARTID_I and PMG_I fields
# of MPAMel_ELx register and otherwise using PARTID_D and PMG_D fields.
# If InSM is True returns MPAM information using PARTID_D and PMG_D fields
# of MPAMSM_EL1 register.
# Produces a PARTID in PARTID space pspace.
MPAMinfo core.genMPAM(core.bits(2) el, boolean InD, boolean InSM, PARTIDspaceType pspace)
    MPAMinfo returninfo;
    PARTIDtype partidel;
    perr = False;
    # gstplk is guest OS application locked by the EL2 hypervisor to
    # only use EL1 the virtual machine's PARTIDs.
    boolean gstplk = (el == EL0 and core.EL2Enabled() and
                      MPAMHCR_EL2.GSTAPP_PLK == '1' and
                      HCR_EL2.TGE == '0');
    core.bits(2) eff_el = EL1 if gstplk else el;
    (partidel, perr) = core.genPARTID(eff_el, InD, InSM);
    PMGtype groupel  = core.genPMG(eff_el, InD, InSM, perr);
    returninfo.mpam_sp = pspace;
    returninfo.partid  = partidel;
    returninfo.pmg     = groupel;
    return returninfo;
# core.GenMPAMatEL()
# =============
# Returns MPAMinfo for the specified EL.
# May be called if MPAM is not implemented (but in an version that supports
# MPAM), MPAM is disabled, or in AArch32.  In AArch32, convert the mode to
# EL if can and use that to drive MPAM information generation.  If mode
# cannot be converted, MPAM is not implemented, or MPAM is disabled return
# default MPAM information for the current security state.
MPAMinfo core.GenMPAMatEL(AccessType acctype, core.bits(2) el)
    mpamEL = 0;
    boolean validEL = False;
    SecurityState security = core.SecurityStateAtEL(el);
    boolean InD = False;
    boolean InSM = False;
    PARTIDspaceType pspace = core.PARTIDspaceFromSS(security);
    if pspace == PIdSpace_NonSecure and not core.MPAMisEnabled():
        return core.DefaultMPAMinfo(pspace);
    if core.UsingAArch32():
        (validEL, mpamEL) = core.ELFromM32(core.APSR.M);
    else:
        mpamEL = EL2 if acctype == AccessType_NV2 else el;
        validEL = True;
    case acctype of
        when AccessType_IFETCH, AccessType_IC
            InD = True;
        when AccessType_SME
            InSM = (boolean IMPLEMENTATION_DEFINED "Shared SMCU" or
                    boolean IMPLEMENTATION_DEFINED "MPAMSM_EL1 label precedence");
        when AccessType_ASIMD
            InSM = (core.HaveSME() and core.APSR.SM == '1' and
                    (boolean IMPLEMENTATION_DEFINED "Shared SMCU" or
                    boolean IMPLEMENTATION_DEFINED "MPAMSM_EL1 label precedence"));
        when AccessType_SVE
            InSM = (core.HaveSME() and core.APSR.SM == '1' and
                    (boolean IMPLEMENTATION_DEFINED "Shared SMCU" or
                    boolean IMPLEMENTATION_DEFINED "MPAMSM_EL1 label precedence"));
        otherwise
            # Other access types are DATA accesses
            InD = False;
    if not validEL:
        return core.DefaultMPAMinfo(pspace);
    elsif core.HaveRME() and MPAMIDR_EL1.HAS_ALTSP == '1':
        # Substitute alternative PARTID space if selected
        pspace = core.AltPARTIDspace(mpamEL, security, pspace);
    if core.HaveMPAMv0p1Ext() and MPAMIDR_EL1.HAS_FORCE_NS == '1':
        if MPAM3_EL3.FORCE_NS == '1' and security == SS_Secure:
            pspace = PIdSpace_NonSecure;
    if (core.HaveMPAMv0p1Ext() or core.HaveMPAMv1p1Ext()) and MPAMIDR_EL1.HAS_SDEFLT == '1':
        if MPAM3_EL3.SDEFLT == '1' and security == SS_Secure:
            return core.DefaultMPAMinfo(pspace);
    if not core.MPAMisEnabled():
        return core.DefaultMPAMinfo(pspace);
    else:
        return core.genMPAM(mpamEL, InD, InSM, pspace);
# core.GenMPAMcurEL()
# ==============
# Returns MPAMinfo for the current EL and security state.
# May be called if MPAM is not implemented (but in an version that supports
# MPAM), MPAM is disabled, or in AArch32.  In AArch32, convert the mode to
# EL if can and use that to drive MPAM information generation.  If mode
# cannot be converted, MPAM is not implemented, or MPAM is disabled return
# default MPAM information for the current security state.
MPAMinfo core.GenMPAMcurEL(AccessType acctype)
    return core.GenMPAMatEL(acctype, core.APSR.EL);
# core.NewAccDesc()
# ============
# Create a new AccessDescriptor with initialised fields
AccessDescriptor core.NewAccDesc(AccessType acctype)
    AccessDescriptor accdesc;
    accdesc.acctype         = acctype;
    accdesc.el              = core.APSR.EL;
    accdesc.ss              = core.SecurityStateAtEL(core.APSR.EL);
    accdesc.acqsc           = False;
    accdesc.acqpc           = False;
    accdesc.relsc           = False;
    accdesc.limitedordered  = False;
    accdesc.exclusive       = False;
    accdesc.rcw             = False;
    accdesc.rcws            = False;
    accdesc.atomicop        = False;
    accdesc.nontemporal     = False;
    accdesc.read            = False;
    accdesc.write           = False;
    accdesc.pan             = False;
    accdesc.nonfault        = False;
    accdesc.firstfault      = False;
    accdesc.first           = False;
    accdesc.contiguous      = False;
    accdesc.streamingsve    = False;
    accdesc.ls64            = False;
    accdesc.mops            = False;
    accdesc.a32lsmd         = False;
    accdesc.tagchecked      = False;
    accdesc.tagaccess       = False;
    accdesc.transactional   = False;
    accdesc.mpam            = core.GenMPAMcurEL(acctype);
    return accdesc;
# core.CreateAccDescSPE()
# ==================
# Access descriptor for memory accesses by Statistical Profiling unit
AccessDescriptor core.CreateAccDescSPE(SecurityState owning_ss, core.bits(2) owning_el)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_SPE);
    accdesc.el              = owning_el;
    accdesc.ss              = owning_ss;
    accdesc.write           = True;
    accdesc.mpam            = core.GenMPAMatEL(AccessType_SPE, owning_el);
    return accdesc;
# core.ConstrainUnpredictableInteger()
# ===============================
# This is a variant of ConstrainUnpredictable for when the result can be Constraint_UNKNOWN.
# If the result is Constraint_UNKNOWN then the function also returns an UNKNOWN
# value in the range low to high, inclusive.
(Constraint,integer) core.ConstrainUnpredictableInteger(integer low, integer high,
                                                   Unpredictable which);
# core.Have52BitVAExt()
# ================
# Returns True if Large Virtual Address extension
# support is implemented and False otherwise.
boolean core.Have52BitVAExt()
    return core.IsFeatureImplemented(FEAT_LVA);
# core.Have56BitVAExt()
# ================
# Returns True if 56-bit Virtual Address extension
# support is implemented and False otherwise.
boolean core.Have56BitVAExt()
    return core.IsFeatureImplemented(FEAT_LVA3);
# core.DebugAddrTop()
# ==============
# Returns the value for the top bit used in Breakpoint and Watchpoint address comparisons.
integer core.DebugAddrTop()
    if core.Have56BitVAExt():
        return 55;
    elsif core.Have52BitVAExt():
        return 52;
    else:
        return 48;
# core.Have16bitVMID()
# ===============
# Returns True if EL2 and support for a 16-bit VMID are implemented.
boolean core.Have16bitVMID()
    return core.IsFeatureImplemented(FEAT_VMID16);
# core.HaveV82Debug()
# ==============
boolean core.HaveV82Debug()
    return core.IsFeatureImplemented(FEAT_Debugv8p2);
# core.HaveDoubleLock()
# ================
# Returns True if support for the OS Double Lock is implemented.
boolean core.HaveDoubleLock()
    return core.IsFeatureImplemented(FEAT_DoubleLock);
# core.DoubleLockStatus()
# ==================
# Returns the state of the OS Double Lock.
#    False if OSDLR_EL1.DLK == 0 or DBGPRCR_EL1.CORENPDRQ == 1 or the PE is in Debug state.
#    True if OSDLR_EL1.DLK == 1 and DBGPRCR_EL1.CORENPDRQ == 0 and the PE is in Non-debug state.
boolean core.DoubleLockStatus()
    if not core.HaveDoubleLock():
        return False;
    elsif core.ELUsingAArch32(EL1):
        return DBGOSDLR.DLK == '1' and DBGPRCR.CORENPDRQ == '0' and not core.Halted();
    else:
        return OSDLR_EL1.DLK == '1' and DBGPRCR_EL1.CORENPDRQ == '0' and not core.Halted();
# core.ExternalRealmInvasiveDebugEnabled()
# ===================================
# The definition of this function is IMPLEMENTATION DEFINED.
# In the recommended interface, this function returns the state of the
# (DBGEN & RLPIDEN) signal.
boolean core.ExternalRealmInvasiveDebugEnabled()
    if not core.HaveRME():
         return False;
    return core.ExternalInvasiveDebugEnabled() and RLPIDEN == HIGH;
# core.ExternalRootInvasiveDebugEnabled()
# ==================================
# The definition of this function is IMPLEMENTATION DEFINED.
# In the recommended interface, this function returns the state of the
# (DBGEN & RLPIDEN & RTPIDEN & SPIDEN) signal when FEAT_SEL2 is implemented
# and the (DBGEN & RLPIDEN & RTPIDEN) signal when FEAT_SEL2 is not implemented.
boolean core.ExternalRootInvasiveDebugEnabled()
    if not core.HaveRME():
         return False;
    return (core.ExternalInvasiveDebugEnabled() and
            (not core.HaveSecureEL2Ext() or core.ExternalSecureInvasiveDebugEnabled()) and
            core.ExternalRealmInvasiveDebugEnabled() and
            RTPIDEN == HIGH);
# core.HaltingAllowed()
# ================
# Returns True if halting is currently allowed, False if halting is prohibited.
boolean core.HaltingAllowed()
    if core.Halted() or core.DoubleLockStatus():
        return False;
    ss = core.CurrentSecurityState();
    case ss of
        when SS_NonSecure return core.ExternalInvasiveDebugEnabled();
        when SS_Secure    return core.ExternalSecureInvasiveDebugEnabled();
        when SS_Root      return core.ExternalRootInvasiveDebugEnabled();
        when SS_Realm     return core.ExternalRealmInvasiveDebugEnabled();
# core.HaltOnBreakpointOrWatchpoint()
# ==============================
# Returns True if the Breakpoint and Watchpoint debug events should be considered for Debug
# state entry, False if they should be considered for a debug exception.
boolean core.HaltOnBreakpointOrWatchpoint()
    return core.HaltingAllowed() and EDSCR.HDE == '1' and OSLSR_EL1.OSLK == '0';
# core.NumBreakpointsImplemented()
# ===========================
# Returns the number of breakpoints implemented. This is indicated to software by
# DBGDIDR.BRPs in AArch32 state, and ID_AA64DFR0_EL1.BRPs in AArch64 state.
integer core.NumBreakpointsImplemented()
    return integer IMPLEMENTATION_DEFINED "Number of breakpoints";
# core.NumWatchpointsImplemented()
# ===========================
# Returns the number of watchpoints implemented. This is indicated to software by
# DBGDIDR.WRPs in AArch32 state, and ID_AA64DFR0_EL1.WRPs in AArch64 state.
integer core.NumWatchpointsImplemented()
    return integer IMPLEMENTATION_DEFINED "Number of watchpoints";
# core.SelfHostedExtendedBPWPEnabled()
# ===============================
# Returns True if the extended breakpoints and watchpoints are enabled, and False otherwise
# from a self-hosted Debug perspective.
boolean core.SelfHostedExtendedBPWPEnabled()
    if core.NumBreakpointsImplemented() <= 16 and core.NumWatchpointsImplemented() <= 16:
        return False;
    if ((core.HaveEL(EL3) and MDCR_EL3.EBWE == '0') or
            (core.EL2Enabled() and MDCR_EL2.EBWE == '0')) then
        return False;
    return MDSCR_EL1.EBWE == '1';
# core.IsBreakpointEnabled()
# =====================
# Returns True if the effective value of DBGBCR_EL1[n].E is '1', and False otherwise.
boolean core.IsBreakpointEnabled(integer n)
    if (n > 15 and
            ((not core.HaltOnBreakpointOrWatchpoint() and not core.SelfHostedExtendedBPWPEnabled()) or
            (core.HaltOnBreakpointOrWatchpoint() and EDSCR2.EBWE == '0'))) then
        return False;
    return DBGBCR_EL1[n].E == '1';
# core.NumContextAwareBreakpointsImplemented()
# =======================================
# Returns the number of context-aware breakpoints implemented. This is indicated to software by
# DBGDIDR.CTX_CMPs in AArch32 state, and ID_AA64DFR0_EL1.CTX_CMPs in AArch64 state.
integer core.NumContextAwareBreakpointsImplemented()
    return integer IMPLEMENTATION_DEFINED "Number of context-aware breakpoints";
# core.ContextMatchingBreakpointRange()
# ================================
# Returns two numbers indicating the index of the first and last context-aware breakpoint.
(integer, integer) core.ContextMatchingBreakpointRange()
    integer b = core.NumBreakpointsImplemented();
    integer c = core.NumContextAwareBreakpointsImplemented();
    if b <= 16:
        return (b - c, b - 1);
    elsif c <= 16:
        return (16 - c, 15);
    else:
        return (0, c - 1);
# core.IsContextMatchingBreakpoint()
# =============================
# Returns True if DBGBCR_EL1[n] is a context-aware breakpoint.
boolean core.IsContextMatchingBreakpoint(integer n)
    (lower, upper) = core.ContextMatchingBreakpointRange();
    return n >= lower and n <= upper;
# core.Ones()
# ======
core.bits(N) core.Ones(integer N)
    return core.Replicate('1',N);
# core.IsOnes()
# ========
boolean core.IsOnes(core.bits(N) x)
    return x == core.Ones(N);
# AArch64.core.BreakpointValueMatch()
# ==============================
boolean AArch64.core.BreakpointValueMatch(integer n_in, core.bits(64) vaddress, boolean linked_to)
    # "n" is the identity of the breakpoint unit to match against.
    # "vaddress" is the current instruction address, ignored if linked_to is True and for Context
    #   matching breakpoints.
    # "linked_to" is True if this is a call from StateMatch for linking.
    integer n = n_in;
    # If a non-existent breakpoint then it is CONSTRAINED raise Exception('UNPREDICTABLE') whether this gives
    # no match or the breakpoint is mapped to another UNKNOWN implemented breakpoint.
    if n >= core.NumBreakpointsImplemented():
        Constraint c;
        (c, n) = core.ConstrainUnpredictableInteger(0, core.NumBreakpointsImplemented() - 1,
                                               Unpredictable_BPNOTIMPL);
        assert c IN {Constraint_DISABLED, Constraint_UNKNOWN};
        if c == Constraint_DISABLED:
             return False;
    # If this breakpoint is not enabled, it cannot generate a match. (This could also happen on a
    # call from StateMatch for linking).
    if not core.IsBreakpointEnabled(n):
         return False;
    context_aware = core.IsContextMatchingBreakpoint(n);
    # If BT is set to a reserved type1, behaves either as disabled or as a not-reserved type1.
    dbgtype = DBGBCR_EL1[n].BT;
    if ((dbgtype IN {'011x','11xx'} and not core.HaveVirtHostExt() and not core.HaveV82Debug()) or # Context matching
          dbgtype IN {'010x'} or                                                 # Reserved
          (not (dbgtype IN {'0x0x'}) and not context_aware) or                          # Context matching
          (dbgtype IN {'1xxx'} and not core.HaveEL(EL2))) then                            # EL2 extension
        Constraint c;
        (c, dbgtype) = core.ConstrainUnpredictableBits(Unpredictable_RESBPTYPE, 4);
        assert c IN {Constraint_DISABLED, Constraint_UNKNOWN};
        if c == Constraint_DISABLED:
             return False;
        # Otherwise the value returned by ConstrainUnpredictableBits must be a not-reserved value
    # Determine what to compare against.
    match_addr = (dbgtype IN {'0x0x'});
    match_vmid = (dbgtype IN {'10xx'});
    match_cid  = (dbgtype IN {'001x'});
    match_cid1 = (dbgtype IN {'101x', 'x11x'});
    match_cid2 = (dbgtype IN {'11xx'});
    linked     = (dbgtype IN {'xxx1'});
    # If this is a call from StateMatch, return False if the breakpoint is not programmed for a
    # VMID and/or context ID match, of if not context-aware. The above assertions mean that the
    # code can just test for match_addr == True to confirm all these things.
    if linked_to and (not linked or match_addr):
         return False;
    # If called from BreakpointMatch return False for Linked context ID and/or VMID matches.
    if not linked_to and linked and not match_addr:
         return False;
    boolean bvr_match  = False;
    boolean bxvr_match = False;
    # Do the comparison.
    if match_addr:
        byte_select_match = False;
        integer byte = core.UInt(core.Field(vaddress,1,0));
        if core.HaveAArch32():
            # T32 instructions can be executed at EL0 in an AArch64 translation regime.
            assert byte IN {0,2};                 # "vaddress" is halfword aligned
            byte_select_match = (DBGBCR_EL1[n].BAS<byte> == '1');
        else:
            assert byte == 0;                     # "vaddress" is word aligned
            byte_select_match = True;             # DBGBCR_EL1[n].BAS<byte> is RES1
        # If the DBGBVR_EL1[n].RESS field bits are not a sign extension of the MSB
        # of DBGBVR_EL1[n].VA, it is raise Exception('UNPREDICTABLE') whether they appear to be
        # included in the match.
        # If 'vaddress' is outside of the current virtual address space, then the access
        # generates a Translation fault.
        integer top = core.DebugAddrTop();
        if not core.IsOnes(DBGBVR_EL1[n]<63:top>) and not core.IsZero(DBGBVR_EL1[n]<63:top>):
            if core.ConstrainUnpredictableBool(Unpredictable_DBGxVR_RESS):
                top = 63;
        bvr_match = (vaddress<top:2> == DBGBVR_EL1[n]<top:2>) and byte_select_match;
    elsif match_cid:
        if core.IsInHost():
            bvr_match = (core.Field(CONTEXTIDR_EL2,31,0) == core.Field(DBGBVR_EL1[n],31,0));
        else:
            bvr_match = (core.APSR.EL IN {EL0, EL1} and core.Field(CONTEXTIDR_EL1,31,0) == core.Field(DBGBVR_EL1[n],31,0));
    elsif match_cid1:
        bvr_match = (core.APSR.EL IN {EL0, EL1} and not core.IsInHost() and
                     core.Field(CONTEXTIDR_EL1,31,0) == core.Field(DBGBVR_EL1[n],31,0));
    if match_vmid:
        vmid = 0;
        bvr_vmid = 0;
        if not core.Have16bitVMID() or VTCR_EL2.VS == '0':
            vmid = core.ZeroExtend(core.Field(VTTBR_EL2.VMID,7,0), 16);
            bvr_vmid = core.ZeroExtend(core.Field(DBGBVR_EL1[n],39,32), 16);
        else:
            vmid     = VTTBR_EL2.VMID;
            bvr_vmid = core.Field(DBGBVR_EL1[n],47,32);
        bxvr_match = (core.APSR.EL IN {EL0, EL1} and core.EL2Enabled() and not core.IsInHost() and vmid == bvr_vmid);
    elsif match_cid2:
        bxvr_match = (core.APSR.EL != EL3 and core.EL2Enabled() and
                      core.Field(DBGBVR_EL1[n],63,32) == core.Field(CONTEXTIDR_EL2,31,0));
    bvr_match_valid  = (match_addr or match_cid or match_cid1);
    bxvr_match_valid = (match_vmid or match_cid2);
    match = (not bxvr_match_valid or bxvr_match) and (not bvr_match_valid or bvr_match);
    return match;
# core.CheckValidStateMatch()
# ======================
# Checks for an invalid state match that will generate Constrained
# Unpredictable behavior, otherwise returns Constraint_NONE.
(Constraint, core.bits(2), bit, bit, core.bits(2)) core.CheckValidStateMatch(core.bits(2) ssc_in, bit ssce_in,
                                                              bit hmc_in, core.bits(2) pxc_in,
                                                              boolean isbreakpnt)
    if not core.HaveRME():
         assert ssce_in == '0';
    boolean reserved = False;
    core.bits(2) ssc = ssc_in;
    bit ssce    = ssce_in;
    bit hmc     = hmc_in;
    core.bits(2) pxc = pxc_in;
    # Values that are not allocated in any architecture version
    case hmc:ssce:ssc:pxc of
        when '0 0 11 10' reserved = True;
        when '0 0 1x xx' reserved = not core.HaveSecureState();
        when '1 0 00 x0' reserved = True;
        when '1 0 01 10' reserved = True;
        when '1 0 1x 10' reserved = True;
        when 'x 1 xx xx' reserved = ssc != '01' or (hmc:pxc) IN {'000','110'};
        otherwise        reserved = False;
    # Match 'Usr/Sys/Svc' valid only for AArch32 breakpoints
    if (not isbreakpnt or not core.HaveAArch32EL(EL1)) and hmc:pxc == '000' and ssc != '11':
        reserved = True;
    # Both EL3 and EL2 are not implemented
    if not core.HaveEL(EL3) and not core.HaveEL(EL2) and (hmc != '0' or ssc != '00'):
        reserved = True;
    # EL3 is not implemented
    if not core.HaveEL(EL3) and ssc IN {'01','10'} and hmc:ssc:pxc != '10100':
        reserved = True;
    # EL3 using AArch64 only
    if (not core.HaveEL(EL3) or not core.HaveAArch64()) and hmc:ssc:pxc == '11000':
        reserved = True;
    # EL2 is not implemented
    if not core.HaveEL(EL2) and hmc:ssc:pxc == '11100':
        reserved = True;
    # Secure EL2 is not implemented
    if not core.HaveSecureEL2Ext() and (hmc:ssc:pxc)  IN {'01100','10100','x11x1'}:
        reserved = True;
    if reserved:
        # If parameters are set to a reserved type1, behaves as either disabled or a defined type1
        Constraint c;
        (c, <hmc,ssc,ssce,pxc>) = core.ConstrainUnpredictableBits(Unpredictable_RESBPWPCTRL, 6);
        assert c IN {Constraint_DISABLED, Constraint_UNKNOWN};
        if c == Constraint_DISABLED:
            return (c, core.bits(2) UNKNOWN, bit UNKNOWN, bit UNKNOWN, core.bits(2) UNKNOWN);
        # Otherwise the value returned by ConstrainUnpredictableBits must be a not-reserved value
    return (Constraint_NONE, ssc, ssce, hmc, pxc);
# AArch64.core.StateMatch()
# ====================
# Determine whether a breakpoint or watchpoint is enabled in the current mode and state.
boolean AArch64.core.StateMatch(core.bits(2) ssc_in, bit ssce_in, bit hmc_in,
                           core.bits(2) pxc_in, boolean linked_in, core.bits(4) lbn,
                           boolean isbreakpnt, AccessDescriptor accdesc)
    if not core.HaveRME():
         assert ssce_in == '0';
    # "ssc_in","ssce_in","hmc_in","pxc_in" are the control fields from
    # the DBGBCR_EL1[n] or DBGWCR_EL1[n] register.
    # "linked_in" is True if this is a linked breakpoint/watchpoint type1.
    # "lbn" is the linked breakpoint number from the DBGBCR_EL1[n] or DBGWCR_EL1[n] register.
    # "isbreakpnt" is True for breakpoints, False for watchpoints.
    # "accdesc" describes the properties of the access being matched.
    core.bits(2) ssc = ssc_in;
    bit ssce    = ssce_in;
    bit hmc     = hmc_in;
    core.bits(2) pxc = pxc_in;
    boolean linked = linked_in;
    # If parameters are set to a reserved type1, behaves as either disabled or a defined type1
    Constraint c;
    (c, ssc, ssce, hmc, pxc) = core.CheckValidStateMatch(ssc, ssce, hmc, pxc, isbreakpnt);
    if c == Constraint_DISABLED:
         return False;
    # Otherwise the hmc,ssc,ssce,pxc values are either valid or the values returned by
    # CheckValidStateMatch are valid.
    EL3_match = core.HaveEL(EL3) and hmc == '1' and core.Bit(ssc,0) == '0';
    EL2_match = core.HaveEL(EL2) and ((hmc == '1' and (ssc:pxc != '1000')) or ssc == '11');
    EL1_match = core.Bit(pxc,0) == '1';
    EL0_match = core.Bit(pxc,1) == '1';
    priv_match = False;
    case accdesc.el of
        when EL3  priv_match = EL3_match;
        when EL2  priv_match = EL2_match;
        when EL1  priv_match = EL1_match;
        when EL0  priv_match = EL0_match;
    # Security state match
    ss_match = False;
    case ssce:ssc of
        when '000' ss_match = hmc == '1' or accdesc.ss != SS_Root;
        when '001' ss_match = accdesc.ss == SS_NonSecure;
        when '010' ss_match = (hmc == '1' and accdesc.ss == SS_Root) or accdesc.ss == SS_Secure;
        when '011' ss_match = (hmc == '1' and accdesc.ss != SS_Root) or accdesc.ss == SS_Secure;
        when '101' ss_match = accdesc.ss == SS_Realm;
    boolean linked_match = False;
    if linked:
        # "lbn" must be an enabled context-aware breakpoint unit. If it is not context-aware then
        # it is CONSTRAINED raise Exception('UNPREDICTABLE') whether this gives no match, gives a match without
        # linking, or lbn is mapped to some UNKNOWN breakpoint that is context-aware.
        integer linked_n = core.UInt(lbn);
        if not core.IsContextMatchingBreakpoint(linked_n):
            (first_ctx_cmp, last_ctx_cmp) = core.ContextMatchingBreakpointRange();
            (c, linked_n) = core.ConstrainUnpredictableInteger(first_ctx_cmp, last_ctx_cmp,
                                                         Unpredictable_BPNOTCTXCMP);
            assert c IN {Constraint_DISABLED, Constraint_NONE, Constraint_UNKNOWN};
            case c of
                when Constraint_DISABLED  return False;      # Disabled
                when Constraint_NONE      linked = False;    # No linking
                # Otherwise ConstrainUnpredictableInteger returned a context-aware breakpoint
        vaddress  = UNKNOWN = 0;
        linked_to = True;
        linked_match = AArch64.core.BreakpointValueMatch(linked_n, vaddress, linked_to);
    return priv_match and ss_match and (not linked or linked_match);
# AArch64.core.BreakpointMatch()
# =========================
# Breakpoint matching in an AArch64 translation regime.
boolean AArch64.core.BreakpointMatch(integer n, core.bits(64) vaddress, AccessDescriptor accdesc,
                                integer size)
    assert not core.ELUsingAArch32(core.S1TranslationRegime());
    assert n < core.NumBreakpointsImplemented();
    enabled = core.IsBreakpointEnabled(n);
    linked  = DBGBCR_EL1[n].BT IN {'0x01'};
    isbreakpnt = True;
    linked_to  = False;
    ssce = DBGBCR_EL1[n].SSCE if core.HaveRME() else '0';
    state_match = AArch64.core.StateMatch(DBGBCR_EL1[n].SSC, ssce, DBGBCR_EL1[n].HMC, DBGBCR_EL1[n].PMC,
                                     linked, DBGBCR_EL1[n].LBN, isbreakpnt, accdesc);
    value_match = AArch64.core.BreakpointValueMatch(n, vaddress, linked_to);
    if core.HaveAArch32() and size == 4:
                            # Check second halfword
        # If the breakpoint address and BAS of an Address breakpoint match the address of the
        # second halfword of an instruction, but not the address of the first halfword, it is
        # CONSTRAINED raise Exception('UNPREDICTABLE') whether or not this breakpoint generates a Breakpoint debug
        # event.
        match_i = AArch64.core.BreakpointValueMatch(n, vaddress + 2, linked_to);
        if not value_match and match_i:
            value_match = core.ConstrainUnpredictableBool(Unpredictable_BPMATCHHALF);
    if core.Bit(vaddress,1) == '1' and DBGBCR_EL1[n].BAS == '1111':
        # The above notwithstanding, if DBGBCR_EL1[n].BAS == '1111',: it is CONSTRAINED
        # raise Exception('UNPREDICTABLE') whether or not a Breakpoint debug event is generated for an instruction
        # at the address DBGBVR_EL1[n]+2.
        if value_match: value_match = core.ConstrainUnpredictableBool(Unpredictable_BPMATCHHALF);
    match = value_match and state_match and enabled;
    return match;
constant core.bits(6) DebugHalt_Breakpoint      = '000111';
constant core.bits(6) DebugHalt_EDBGRQ          = '010011';
constant core.bits(6) DebugHalt_Step_Normal     = '011011';
constant core.bits(6) DebugHalt_Step_Exclusive  = '011111';
constant core.bits(6) DebugHalt_OSUnlockCatch   = '100011';
constant core.bits(6) DebugHalt_ResetCatch      = '100111';
constant core.bits(6) DebugHalt_Watchpoint      = '101011';
constant core.bits(6) DebugHalt_HaltInstruction = '101111';
constant core.bits(6) DebugHalt_SoftwareAccess  = '110011';
constant core.bits(6) DebugHalt_ExceptionCatch  = '110111';
constant core.bits(6) DebugHalt_Step_NoSyndrome = '111011';
# CrossTrigger
# ============
enumeration CrossTriggerOut {CrossTriggerOut_DebugRequest, CrossTriggerOut_RestartRequest,
                             CrossTriggerOut_IRQ,          CrossTriggerOut_RSVD3,
                             CrossTriggerOut_TraceExtIn0,  CrossTriggerOut_TraceExtIn1,
                             CrossTriggerOut_TraceExtIn2,  CrossTriggerOut_TraceExtIn3};
enumeration CrossTriggerIn  {CrossTriggerIn_CrossHalt,     CrossTriggerIn_PMUOverflow,
                             CrossTriggerIn_RSVD2,         CrossTriggerIn_RSVD3,
                             CrossTriggerIn_TraceExtOut0,  CrossTriggerIn_TraceExtOut1,
                             CrossTriggerIn_TraceExtOut2,  CrossTriggerIn_TraceExtOut3};
# core.CTI_SignalEvent()
# =================
# Signal a discrete event on a Cross Trigger input event trigger.
core.CTI_SignalEvent(CrossTriggerIn id);
# core.ClearExclusiveLocal()
# =====================
# Clear the local Exclusives monitor for the specified processorid.
core.ClearExclusiveLocal(integer processorid);
# core.DiscardTransactionalWrites()
# ============================
# Discards all transactional writes to memory and reset the transactional
# read and write sets.
core.DiscardTransactionalWrites();
# core.HaveBRBExt()
# ============
# Returns True if Branch Record Buffer Extension is implemented, and False otherwise.
boolean core.HaveBRBExt()
    return core.IsFeatureImplemented(FEAT_BRBE);
# core.ProcessorID()
# =============
# Return the ID of the currently executing PE.
integer core.ProcessorID();
# core.Align()
# =======
integer core.Align(integer x, integer y)
    return y * (x DIV y);
# core.Align()
# =======
core.bits(N) core.Align(core.bits(N) x, integer y)
    return core.Align(core.UInt(x), y)<N-1:0>;
# core.FloorPow2()
# ===========
# For a positive integer X, return the largest power of 2 <= X
integer core.FloorPow2(integer x)
    assert x >= 0;
    integer n = 1;
    if x == 0:
         return 0;
    while x >= 2^n do
        n = n + 1;
    return 2^(n - 1);
# core.CeilPow2()
# ==========
# For a positive integer X, return the smallest power of 2 >= X
integer core.CeilPow2(integer x)
    if x == 0:
         return 0;
    if x == 1:
         return 2;
    return core.FloorPow2(x - 1) * 2;
# core.IsPow2()
# ========
# Return True if positive integer X is a power of 2. Otherwise,
# return False.
boolean core.IsPow2(integer x)
    if x <= 0:
         return False;
    return core.FloorPow2(x) == core.CeilPow2(x);
# core.MaxImplementedVL()
# ==================
integer core.MaxImplementedVL()
    return integer IMPLEMENTATION_DEFINED "Max implemented VL";
# core.Min()
# =====
integer core.Min(integer a, integer b)
    return a if a <= b else b;
# core.Min()
# =====
real core.Min(real a, real b)
    return a if a <= b else b;
# core.ImplementedSVEVectorLength()
# ============================
# Reduce SVE vector length to a supported value (power of two)
integer core.ImplementedSVEVectorLength(integer nbits_in)
    integer maxbits = core.MaxImplementedVL();
    assert 128 <= maxbits and maxbits <= 2048 and core.IsPow2(maxbits);
    integer nbits = core.Min(nbits_in, maxbits);
    assert 128 <= nbits and nbits <= 2048 and core.Align(nbits, 128) == nbits;
    while nbits > 128 do
        if core.IsPow2(nbits):
             return nbits;
        nbits = nbits - 128;
    return nbits;
# CurrentNSVL - non-assignment form
# =================================
# Non-Streaming VL
integer CurrentNSVL
    vl = 0;
    if core.APSR.EL == EL1 or (core.APSR.EL == EL0 and not core.IsInHost()):
        vl = core.UInt(ZCR_EL1.LEN);
    if core.APSR.EL == EL2 or (core.APSR.EL == EL0 and core.IsInHost()):
        vl = core.UInt(ZCR_EL2.LEN);
    elsif core.APSR.EL IN {EL0, EL1} and core.EL2Enabled():
        vl = core.Min(vl, core.UInt(ZCR_EL2.LEN));
    if core.APSR.EL == EL3:
        vl = core.UInt(ZCR_EL3.LEN);
    elsif core.HaveEL(EL3):
        vl = core.Min(vl, core.UInt(ZCR_EL3.LEN));
    vl = (vl + 1) * 128;
    vl = core.ImplementedSVEVectorLength(vl);
    return vl;
# core.MaxImplementedSVL()
# ===================
integer core.MaxImplementedSVL()
    return integer IMPLEMENTATION_DEFINED "Max implemented SVL";
# core.SupportedPowerTwoSVL()
# ======================
# Return an IMPLEMENTATION DEFINED specific value
# returns True if SVL is supported and is a power of two, False otherwise
boolean core.SupportedPowerTwoSVL(integer nbits);
# core.ImplementedSMEVectorLength()
# ============================
# Reduce SVE/SME vector length to a supported value (power of two)
integer core.ImplementedSMEVectorLength(integer nbits_in)
    integer maxbits = core.MaxImplementedSVL();
    assert 128 <= maxbits and maxbits <= 2048 and core.IsPow2(maxbits);
    integer nbits = core.Min(nbits_in, maxbits);
    assert 128 <= nbits and nbits <= 2048 and core.Align(nbits, 128) == nbits;
    # Search for a supported power-of-two VL less than or equal to nbits
    while nbits > 128 do
        if core.IsPow2(nbits) and core.SupportedPowerTwoSVL(nbits):
             return nbits;
        nbits = nbits - 128;
    # Return the smallest supported power-of-two VL
    nbits = 128;
    while nbits < maxbits do
        if core.SupportedPowerTwoSVL(nbits):
             return nbits;
        nbits = nbits * 2;
    # The only option is maxbits
    return maxbits;
# CurrentSVL - non-assignment form
# ================================
# Streaming SVL
integer CurrentSVL
    vl = 0;
    if core.APSR.EL == EL1 or (core.APSR.EL == EL0 and not core.IsInHost()):
        vl = core.UInt(SMCR_EL1.LEN);
    if core.APSR.EL == EL2 or (core.APSR.EL == EL0 and core.IsInHost()):
        vl = core.UInt(SMCR_EL2.LEN);
    elsif core.APSR.EL IN {EL0, EL1} and core.EL2Enabled():
        vl = core.Min(vl, core.UInt(SMCR_EL2.LEN));
    if core.APSR.EL == EL3:
        vl = core.UInt(SMCR_EL3.LEN);
    elsif core.HaveEL(EL3):
        vl = core.Min(vl, core.UInt(SMCR_EL3.LEN));
    vl = (vl + 1) * 128;
    vl = core.ImplementedSMEVectorLength(vl);
    return vl;
# CurrentVL - non-assignment form
# ===============================
integer CurrentVL
    return CurrentSVL if core.HaveSME() and core.APSR.SM == '1' else CurrentNSVL;
constant integer MAX_VL = 2048;
constant integer MAX_PL = 256;
constant integer ZT0_LEN =  512;
core.bits(MAX_PL) _FFR;
array core.bits(MAX_VL) _Z[0..31];
array core.bits(MAX_PL) _P[0..15];
# FFR[] - non-assignment form
# ===========================
core.bits(width) FFcore.R[integer width]
    assert width == CurrentVL DIV 8;
    return _FFR<width-1:0>;
# FFR[] - assignment form
# =======================
FFcore.R[integer width] = core.bits(width) value
    assert width == CurrentVL DIV 8;
    if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
        _FFR = core.ZeroExtend(value, MAX_PL);
    else:
        _FFR<width-1:0> = value;
# AArch64.core.IsFPEnabled()
# =====================
# Returns True if access to the SIMD&FP instructions or System registers are
# enabled at the target exception level in AArch64 state and False otherwise.
boolean AArch64.core.IsFPEnabled(core.bits(2) el)
    # Check if access disabled in CPACR_EL1
    if el IN {EL0, EL1} and not core.IsInHost():
        # Check SIMD&FP at EL0/EL1
        disabled = False;
        case CPACR_EL1.FPEN of
            when 'x0' disabled = True;
            when '01' disabled = el == EL0;
            when '11' disabled = False;
        if disabled:
             return False;
    # Check if access disabled in CPTR_EL2
    if el IN {EL0, EL1, EL2} and core.EL2Enabled():
        if core.HaveVirtHostExt() and HCR_EL2.E2H == '1':
            disabled = False;
            case CPTR_EL2.FPEN of
                when 'x0' disabled = True;
                when '01' disabled = el == EL0 and HCR_EL2.TGE == '1';
                when '11' disabled = False;
            if disabled:
                 return False;
        else:
            if CPTR_EL2.TFP == '1':
                 return False;
    # Check if access disabled in CPTR_EL3
    if core.HaveEL(EL3):
        if CPTR_EL3.TFP == '1': return False;
    return True;
# core.IsFPEnabled()
# =====================
# Returns True if access to the SIMD&FP instructions or System registers are
# enabled at the target exception level in AArch32 state and False otherwise.
boolean core.IsFPEnabled(core.bits(2) el)
    if el == EL0 and not core.ELUsingAArch32(EL1):
        return AArch64.core.IsFPEnabled(el);
    if core.HaveEL(EL3) and core.ELUsingAArch32(EL3) and core.CurrentSecurityState() == SS_NonSecure:
        # Check if access disabled in NSACR
        if NSACR.cp10 == '0': return False;
    if el IN {EL0, EL1}:
        # Check if access disabled in CPACR
        disabled = False;
        case CPACR.cp10 of
            when '00' disabled = True;
            when '01' disabled = el == EL0;
            when '10' disabled = core.ConstrainUnpredictableBool(Unpredictable_RESCPACR);
            when '11' disabled = False;
        if disabled:
             return False;
    if el IN {EL0, EL1, EL2} and core.EL2Enabled():
        if not core.ELUsingAArch32(EL2):
            return AArch64.core.IsFPEnabled(EL2);
        if HCPTR.TCP10 == '1':
             return False;
    if core.HaveEL(EL3) and not core.ELUsingAArch32(EL3):
        # Check if access disabled in CPTR_EL3
        if CPTR_EL3.TFP == '1': return False;
    return True;
# core.IsFPEnabled()
# =============
# Returns True if accesses to the Advanced SIMD and floating-point
# registers are enabled at the target exception level in the current
# execution state and False otherwise.
boolean core.IsFPEnabled(core.bits(2) el)
    if core.ELUsingAArch32(el):
        return core.IsFPEnabled(el);
    else:
        return AArch64.core.IsFPEnabled(el);
# core.IsOriginalSVEEnabled()
# ======================
# Returns True if access to SVE functionality is enabled at the target
# exception level and False otherwise.
boolean core.IsOriginalSVEEnabled(core.bits(2) el)
    disabled = False;
    if core.ELUsingAArch32(el):
        return False;
    # Check if access disabled in CPACR_EL1
    if el IN {EL0, EL1} and not core.IsInHost():
        # Check SVE at EL0/EL1
        case CPACR_EL1.ZEN of
            when 'x0' disabled = True;
            when '01' disabled = el == EL0;
            when '11' disabled = False;
        if disabled:
             return False;
    # Check if access disabled in CPTR_EL2
    if el IN {EL0, EL1, EL2} and core.EL2Enabled():
        if core.HaveVirtHostExt() and HCR_EL2.E2H == '1':
            case CPTR_EL2.ZEN of
                when 'x0' disabled = True;
                when '01' disabled = el == EL0 and HCR_EL2.TGE == '1';
                when '11' disabled = False;
            if disabled:
                 return False;
        else:
            if CPTR_EL2.TZ == '1':
                 return False;
    # Check if access disabled in CPTR_EL3
    if core.HaveEL(EL3):
        if CPTR_EL3.EZ == '0': return False;
    return True;
# core.IsSMEEnabled()
# ==============
# Returns True if access to SME functionality is enabled at the target
# exception level and False otherwise.
boolean core.IsSMEEnabled(core.bits(2) el)
    disabled = False;
    if core.ELUsingAArch32(el):
        return False;
    # Check if access disabled in CPACR_EL1
    if el IN {EL0, EL1} and not core.IsInHost():
        # Check SME at EL0/EL1
        case CPACR_EL1.SMEN of
            when 'x0' disabled = True;
            when '01' disabled = el == EL0;
            when '11' disabled = False;
        if disabled:
             return False;
    # Check if access disabled in CPTR_EL2
    if el IN {EL0, EL1, EL2} and core.EL2Enabled():
        if core.HaveVirtHostExt() and HCR_EL2.E2H == '1':
            case CPTR_EL2.SMEN of
                when 'x0' disabled = True;
                when '01' disabled = el == EL0 and HCR_EL2.TGE == '1';
                when '11' disabled = False;
            if disabled:
                 return False;
        else:
            if CPTR_EL2.TSM == '1':
                 return False;
    # Check if access disabled in CPTR_EL3
    if core.HaveEL(EL3):
        if CPTR_EL3.ESM == '0': return False;
    return True;
# core.IsSVEEnabled()
# ==============
# Returns True if access to SVE registers is enabled at the target exception
# level and False otherwise.
boolean core.IsSVEEnabled(core.bits(2) el)
    if core.HaveSME() and core.APSR.SM == '1':
        return core.IsSMEEnabled(el);
    elsif core.HaveSVE():
        return core.IsOriginalSVEEnabled(el);
    else:
        return False;
# P[] - non-assignment form
# =========================
core.bits(width) P[integer n, integer width]
    assert n >= 0 and n <= 31;
    assert width == CurrentVL DIV 8;
    return _P[n]<width-1:0>;
# P[] - assignment form
# =====================
P[integer n, integer width] = core.bits(width) value
    assert n >= 0 and n <= 31;
    assert width == CurrentVL DIV 8;
    if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
        _P[n] = core.ZeroExtend(value, MAX_PL);
    else:
        _P[n]<width-1:0> = value;
# SP[] - assignment form
# ======================
# Write to stack pointer from a 64-bit value.
SP[] = core.bits(64) value
    if core.APSR.SP == '0':
        SP_EL0 = value;
    else:
        case core.APSR.EL of
            when EL0  SP_EL0 = value;
            when EL1  SP_EL1 = value;
            when EL2  SP_EL2 = value;
            when EL3  SP_EL3 = value;
    return;
# SP[] - non-assignment form
# ==========================
# Read stack pointer with slice of 64 bits.
core.bits(64) SP[]
    if core.APSR.SP == '0':
        return SP_EL0;
    else:
        case core.APSR.EL of
            when EL0  return SP_EL0;
            when EL1  return SP_EL1;
            when EL2  return SP_EL2;
            when EL3  return SP_EL3;
# TMState
# =======
# Transactional execution state bits.
# There is no significance to the field order.
type TMState is (
    integer       depth,              # Transaction nesting depth
    integer       Rt,                 # TSTART destination register
    core.bits(64)      nPC,                # Fallback instruction address
    array[0..30] of core.bits(64)     X,   # General purpose registers
    array[0..31] of core.bits(MAX_VL) Z,   # Vector registers
    array[0..15] of core.bits(MAX_PL) P,   # Predicate registers
    core.bits(MAX_PL)  FFR,                # First Fault Register
    core.bits(64)      SP,                 # Stack Pointer at current EL
    core.bits(64)      FPCR,               # Floating-point Control Register
    core.bits(64)      FPSR,               # Floating-point Status Register
    core.bits(64)      ICC_PMR_EL1,        # Interrupt Controller Interrupt Priority Mask Register
    core.bits(64)      GCSPR_ELx,          # GCS pointer for current EL
    core.bits(4)       nzcv,               # Condition flags
    core.bits(1)       D,                  # Debug mask bit
    core.bits(1)       A,                  # SError interrupt mask bit
    core.bits(1)       I,                  # IRQ mask bit
    core.bits(1)       F                   # FIQ mask bit
)
TMState TSTATE;
# V[] - assignment form
# =====================
# Write to SIMD&FP register with implicit extension from
# 8, 16, 32, 64 or 128 bits.
V[integer n, integer width] = core.bits(width) value
    assert n >= 0 and n <= 31;
    assert width IN {8,16,32,64,128};
    integer vlen = CurrentVL if core.IsSVEEnabled(core.APSR.EL) else 128;
    if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
        _Z[n] = core.ZeroExtend(value, MAX_VL);
    else:
        _Z[n]<vlen-1:0> = core.ZeroExtend(value, vlen);
# V[] - non-assignment form
# =========================
# Read from SIMD&FP register with implicit slice of 8, 16
# 32, 64 or 128 bits.
core.bits(width) V[integer n, integer width]
    assert n >= 0 and n <= 31;
    assert width IN {8,16,32,64,128};
    return _Z[n]<width-1:0>;
# _R[] - the general-purpose register file
# ========================================
array core.bits(64) _core.R[0..30];
# X[] - assignment form
# =====================
# Write to general-purpose register from either a 32-bit or a 64-bit value,
# where the size of the value is passed as an argument.
X[integer n, integer width] = core.bits(width) value
    assert n >= 0 and n <= 31;
    assert width IN {32,64};
    if n != 31:
        _core.R[n] = core.ZeroExtend(value, 64);
    return;
# X[] - non-assignment form
# =========================
# Read from general-purpose register with an explicit slice of 8, 16, 32 or 64 bits.
core.bits(width) X[integer n, integer width]
    assert n >= 0 and n <= 31;
    assert width IN {8,16,32,64};
    if n != 31:
        return _core.readR(n)<width-1:0>;
    else:
        return core.Zeros(width);
# Z[] - non-assignment form
# =========================
core.bits(width) Z[integer n, integer width]
    assert n >= 0 and n <= 31;
    assert width == CurrentVL;
    return _Z[n]<width-1:0>;
# Z[] - assignment form
# =====================
Z[integer n, integer width] = core.bits(width) value
    assert n >= 0 and n <= 31;
    assert width == CurrentVL;
    if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
        _Z[n] = core.ZeroExtend(value, MAX_VL);
    else:
        _Z[n]<width-1:0> = value;
# core.RestoreTransactionCheckpoint()
# ==============================
# Restores part of the PE registers from the transaction checkpoint.
core.RestoreTransactionCheckpoint()
    SP[]             = TSTATE.SP;
    ICC_PMR_EL1      = TSTATE.ICC_PMR_EL1;
    core.APSR.<N,Z,C,V> = TSTATE.nzcv;
    core.APSR.<D,A,I,F> = TSTATE.<D,A,I,F>;
    for n in range(0,30+1):
        X[n, 64] = TSTATE.X[n];
    if core.IsFPEnabled(core.APSR.EL):
        if core.IsSVEEnabled(core.APSR.EL):
            constant integer VL = CurrentVL;
            constant integer PL = VL DIV 8;
            for n in range(0,31+1):
                Z[n, VL] = TSTATE.Z[n]<VL-1:0>;
            for n in range(0,15+1):
                P[n, PL] = TSTATE.P[n]<PL-1:0>;
            FFcore.R[PL] = TSTATE.FFR<PL-1:0>;
        else:
            for n in range(0,31+1):
                V[n, 128] = core.Field(TSTATE.Z[n],127,0);
        FPCR = TSTATE.FPCR;
        FPSR = TSTATE.FPSR;
    case core.APSR.EL of
        when EL0 GCSPR_EL0 = TSTATE.GCSPR_ELx;
        when EL1 GCSPR_EL1 = TSTATE.GCSPR_ELx;
        when EL2 GCSPR_EL2 = TSTATE.GCSPR_ELx;
        when EL3 GCSPR_EL3 = TSTATE.GCSPR_ELx;
    return;
# TMFailure
# =========
# Transactional failure causes
enumeration TMFailure {
    TMFailure_CNCL,    # Executed a TCANCEL instruction
    TMFailure_DBG,     # A debug event was generated
    TMFailure_ERR,     # A non-permissible operation was attempted
    TMFailure_NEST,    # The maximum transactional nesting level was exceeded
    TMFailure_SIZE,    # The transactional read or write set limit was exceeded
    TMFailure_MEM,     # A transactional conflict occurred
    TMFailure_TRIVIAL, # Only a TRIVIAL version of TM is available
    TMFailure_IMP      # Any other failure cause
};
# core.FailTransaction()
# =================
core.FailTransaction(TMFailure cause, boolean retry)
    core.FailTransaction(cause, retry, False, core.Zeros(15));
    return;
# core.FailTransaction()
# =================
# Exits Transactional state and discards transactional updates to registers
# and memory.
core.FailTransaction(TMFailure cause, boolean retry, boolean interrupt, core.bits(15) reason)
    assert not retry or not interrupt;
    if core.HaveBRBExt() and core.BranchRecordAllowed(core.APSR.EL):
         BRBFCR_EL1.LASTFAILED = '1';
    core.DiscardTransactionalWrites();
    # For trivial implementation no transaction checkpoint was taken
    if cause != TMFailure_TRIVIAL:
        core.RestoreTransactionCheckpoint();
    core.ClearExclusiveLocal(core.ProcessorID());
    core.bits(64) result = core.Zeros(64);
    result = core.SetBit(result,23,'1' if interrupt else '0')
    result = core.SetBit(result,15,'1' if retry and not interrupt else '0')
    case cause of
        when TMFailure_TRIVIAL result = core.SetBit(result,24,'1')
        when TMFailure_DBG     result = core.SetBit(result,22,'1')
        when TMFailure_NEST    result = core.SetBit(result,21,'1')
        when TMFailure_SIZE    result = core.SetBit(result,20,'1')
        when TMFailure_ERR     result = core.SetBit(result,19,'1')
        when TMFailure_IMP     result = core.SetBit(result,18,'1')
        when TMFailure_MEM     result = core.SetBit(result,17,'1')
        when TMFailure_CNCL    result = core.SetBit(result,16,'1'; result = core.SetField(result,14,0,reason))
    TSTATE.depth = 0;
    X[TSTATE.Rt, 64] = core.Field(result);
    boolean branch_conditional = False;
    core.BranchTo(TSTATE.nPC, 'TMFAIL', branch_conditional);
    core.EndOfInstruction();
    return;
# core.HaveBTIExt()
# ============
# Returns True if support for Branch Target Indentification is implemented.
boolean core.HaveBTIExt()
    return core.IsFeatureImplemented(FEAT_BTI);
# core.HaveDITExt()
# ============
boolean core.HaveDITExt()
    return core.IsFeatureImplemented(FEAT_DIT);
# core.HaveFeatNMI()
# =============
# Returns True if the Non-Maskable Interrupt extension is
# implemented, and False otherwise.
boolean core.HaveFeatNMI()
    return core.IsFeatureImplemented(FEAT_NMI);
# core.HaveGCS()
# =========
# Returns True if support for Guarded Control Stack is
# implemented, and False otherwise.
boolean core.HaveGCS()
    return core.IsFeatureImplemented(FEAT_GCS);
# core.HaveMTEExt()
# ============
# Returns True if instruction-only MTE implemented, and False otherwise.
boolean core.HaveMTEExt()
    return core.IsFeatureImplemented(FEAT_MTE);
# core.HavePANExt()
# ============
boolean core.HavePANExt()
    return core.IsFeatureImplemented(FEAT_PAN);
# core.HaveUAOExt()
# ============
boolean core.HaveUAOExt()
    return core.IsFeatureImplemented(FEAT_UAO);
# core.GetPSRFromcore.APSR()
# ==================
# Return a PSR value which represents the current core.APSR
core.bits(N) core.GetPSRFromcore.APSR(ExceptionalOccurrenceTargetState targetELState, integer N)
    if core.UsingAArch32() and targetELState == AArch32_NonDebugState:
        assert N == 32;
    else:
        assert N == 64;
    core.bits(N) spsr = core.Zeros(N);
    spsr = core.SetField(spsr,31,28,core.APSR.<N,Z,C,V>);
    if core.HavePANExt():
         spsr = core.SetBit(spsr,22,core.APSR.PAN)
    spsr = core.SetBit(spsr,20,core.APSR.IL)
    if core.APSR.nRW == '1':
                                   # AArch32 state
        spsr = core.SetBit(spsr,27,core.APSR.Q)
        spsr = core.SetField(spsr,26,25,core.Field(core.APSR.IT,1,0));
        if core.HaveSSBSExt():
             spsr = core.SetBit(spsr,23,core.APSR.SSBS)
        if core.HaveDITExt():
            if targetELState == AArch32_NonDebugState:
                spsr = core.SetBit(spsr,21,core.APSR.DIT)
            else                                        # AArch64_NonDebugState or DebugState
                spsr = core.SetBit(spsr,24,core.APSR.DIT)
        if targetELState IN {AArch64_NonDebugState, DebugState}:
            spsr = core.SetBit(spsr,21,core.APSR.SS)
        spsr = core.SetField(spsr,19,16,core.APSR.GE);
        spsr = core.SetField(spsr,15,10,core.Field(core.APSR.IT,7,2));
        spsr = core.SetBit(spsr,9,core.APSR.E)
        spsr = core.SetField(spsr,8,6,core.APSR.<A,I,F>);                   # No core.APSR.D in AArch32 state
        spsr = core.SetBit(spsr,5,core.APSR.T)
        assert core.Bit(core.APSR.M,4) == core.APSR.nRW;               # bit [4] is the discriminator
        spsr = core.SetField(spsr,4,0,core.APSR.M);
    else                                                # AArch64 state
        if core.HaveMTEExt():
             spsr = core.SetBit(spsr,25,core.APSR.TCO)
        if core.HaveGCS():
             spsr = core.SetBit(spsr,34,core.APSR.EXLOCK)
        if core.HaveDITExt():
             spsr = core.SetBit(spsr,24,core.APSR.DIT)
        if core.HaveUAOExt():
             spsr = core.SetBit(spsr,23,core.APSR.UAO)
        spsr = core.SetBit(spsr,21,core.APSR.SS)
        if core.HaveFeatNMI():
             spsr = core.SetBit(spsr,13,core.APSR.ALLINT)
        if core.HaveSSBSExt():
             spsr = core.SetBit(spsr,12,core.APSR.SSBS)
        if core.HaveBTIExt():
             spsr = core.SetField(spsr,11,10,core.APSR.BTYPE);
        spsr = core.SetField(spsr,9,6,core.APSR.<D,A,I,F>);
        spsr = core.SetBit(spsr,4,core.APSR.nRW)
        spsr = core.SetField(spsr,3,2,core.APSR.EL);
        spsr = core.SetBit(spsr,0,core.APSR.SP)
    return spsr;
# core.Havev8p9Debug()
# ===============
# Returns True if support for the Debugv8p9 feature is implemented, and False otherwise.
boolean core.Havev8p9Debug()
    return core.IsFeatureImplemented(FEAT_Debugv8p9);
# core.StopInstructionPrefetchAndEnableITR()
# =====================================
core.StopInstructionPrefetchAndEnableITR();
# core.ThisInstrAddr()
# ===============
# Return address of the current instruction.
core.bits(N) core.ThisInstrAddr(integer N)
    assert N == 64 or (N == 32 and core.UsingAArch32());
    return _PC<N-1:0>;
# core.Halt()
# ======
core.Halt(core.bits(6) reason)
    boolean is_async = False;
    core.Halt(reason, is_async);
# core.Halt()
# ======
core.Halt(core.bits(6) reason, boolean is_async)
    if core.HaveTME() and TSTATE.depth > 0:
        core.FailTransaction(TMFailure_DBG, False);
    core.CTI_SignalEvent(CrossTriggerIn_CrossHalt);  # Trigger other cores to halt
    core.bits(64) preferred_restart_address = core.ThisInstrAddr(64);
    core.bits(64) spsr = core.GetPSRFromcore.APSR(DebugState, 64);
    if (core.HaveBTIExt() and not is_async and not (reason IN {DebugHalt_Step_Normal, DebugHalt_Step_Exclusive,
        DebugHalt_Step_NoSyndrome, DebugHalt_Breakpoint, DebugHalt_HaltInstruction}) and
        core.ConstrainUnpredictableBool(Unpredictable_ZEROBTYPE)) then
        spsr = core.SetField(spsr,11,10,'00');
    if core.UsingAArch32():
        DLR = core.Field(preferred_restart_address,31,0);
        DSPSR = core.Field(spsr,31,0);
        if core.Havev8p9Debug():
            DSPSR2 = core.Field(spsr,63,32);
    else:
        DLR_EL0 = preferred_restart_address;
        DSPSR_EL0 = spsr;
    EDSCR.ITE = '1';
    EDSCR.ITO = '0';
    if core.HaveRME():
        EDSCR.SDD = '0' if core.ExternalRootInvasiveDebugEnabled() else '1';
    elsif core.CurrentSecurityState() == SS_Secure:
        EDSCR.SDD = '0';                        # If entered in Secure state, allow debug
    elsif core.HaveEL(EL3):
        EDSCR.SDD = '0' if core.ExternalSecureInvasiveDebugEnabled() else '1';
    else:
        EDSCR.SDD = '1';                        # Otherwise EDSCR.SDD is RES1
    EDSCR.MA = '0';
    # In Debug state:
    # * core.APSR.{SS,SSBS,D,A,I,F} are not observable and ignored so behave-as-if UNKNOWN.
    # * core.APSR.{N,Z,C,V,Q,GE,E,M,nRW,EL,SP,DIT} are also not observable, but since these
    #     are not changed on exception entry, this function also leaves them unchanged.
    # * core.APSR.{IT,T} are ignored.
    # * core.APSR.IL is ignored and behave-as-if 0.
    # * core.APSR.BTYPE is ignored and behave-as-if 0.
    # * core.APSR.TCO is set 1.
    # * core.APSR.{UAO,PAN} are observable and not changed on entry into Debug state.
    if core.UsingAArch32():
        core.APSR.<IT,SS,SSBS,A,I,F,T> = UNKNOWN = 0;
    else:
        core.APSR.<SS,SSBS,D,A,I,F>    = core.bits(6)  UNKNOWN;
        core.APSR.TCO = '1';
        core.APSR.BTYPE = '00';
    core.APSR.IL = '0';
    core.StopInstructionPrefetchAndEnableITR();
    EDSCR.STATUS = reason;                      # Signal entered Debug state
    core.UpdateEDSCRFields();                        # Update EDSCR PE state flags.
    return;
# AArch64.core.CheckBreakpoint()
# =========================
# Called before executing the instruction of length "size" bytes at "vaddress" in an AArch64
# translation regime, when either debug exceptions are enabled, or halting debug is enabled
# and halting is allowed.
FaultRecord AArch64.core.CheckBreakpoint(FaultRecord fault_in, core.bits(64) vaddress,
                                    AccessDescriptor accdesc, integer size)
    assert not core.ELUsingAArch32(core.S1TranslationRegime());
    assert (core.UsingAArch32() and size IN {2,4}) or size == 4;
    FaultRecord fault = fault_in;
    for i = 0 to core.NumBreakpointsImplemented() - 1
        if AArch64.core.BreakpointMatch(i, vaddress, accdesc, size):
            fault.statuscode = Fault_Debug;
    if fault.statuscode == Fault_Debug and core.HaltOnBreakpointOrWatchpoint():
        reason = DebugHalt_Breakpoint;
        core.Halt(reason);
    return fault;
# AArch64.core.WatchpointByteMatch()
# =============================
boolean AArch64.core.WatchpointByteMatch(integer n, core.bits(64) vaddress)
    integer top = core.DebugAddrTop();
    bottom = 2 if DBGWVR_EL1[n]<2> == '1' else 3;            # Word or doubleword
    byte_select_match = (DBGWCR_EL1[n].BAS<core.UInt(vaddress<bottom-1:0>)> != '0');
    mask = core.UInt(DBGWCR_EL1[n].MASK);
    # If DBGWCR_EL1[n].MASK is non-zero value and DBGWCR_EL1[n].BAS is not set to '11111111', or
    # DBGWCR_EL1[n].BAS specifies a non-contiguous set of bytes behavior is CONSTRAINED
    # raise Exception('UNPREDICTABLE').
    if mask > 0 and not core.IsOnes(DBGWCR_EL1[n].BAS):
        byte_select_match = core.ConstrainUnpredictableBool(Unpredictable_WPMASK&BAS);
    else:
        LSB = (DBGWCR_EL1[n].BAS & core.NOT(DBGWCR_EL1[n].BAS - 1));  MSB = (DBGWCR_EL1[n].BAS + LSB);
        if not core.IsZero(MSB & (MSB - 1)):
                                 # Not contiguous
            byte_select_match = core.ConstrainUnpredictableBool(Unpredictable_WPBASCONTIGUOUS);
            bottom = 3;                                        # For the whole doubleword
    # If the address mask is set to a reserved value, the behavior is CONSTRAINED raise Exception('UNPREDICTABLE').
    if mask > 0 and mask <= 2:
        Constraint c;
        (c, mask) = core.ConstrainUnpredictableInteger(3, 31, Unpredictable_RESWPMASK);
        assert c IN {Constraint_DISABLED, Constraint_NONE, Constraint_UNKNOWN};
        case c of
            when Constraint_DISABLED  return False;            # Disabled
            when Constraint_NONE      mask = 0;                # No masking
            # Otherwise the value returned by ConstrainUnpredictableInteger is a not-reserved value
    WVR_match = False;
    if mask > bottom:
        # If the DBGxVR<n>_EL1.RESS field bits are not a sign extension of the MSB
        # of DBGxVR<n>_EL1.VA, it is raise Exception('UNPREDICTABLE') whether they appear to be
        # included in the match.
        if not core.IsOnes(DBGWVR_EL1[n]<63:top>) and not core.IsZero(DBGWVR_EL1[n]<63:top>):
            if core.ConstrainUnpredictableBool(Unpredictable_DBGxVR_RESS):
                top = 63;
        WVR_match = (vaddress<top:mask> == DBGWVR_EL1[n]<top:mask>);
        # If masked bits of DBGWVR_EL1[n] are not zero, the behavior is CONSTRAINED raise Exception('UNPREDICTABLE').
        if WVR_match and not core.IsZero(DBGWVR_EL1[n]<mask-1:bottom>):
            WVR_match = core.ConstrainUnpredictableBool(Unpredictable_WPMASKEDBITS);
    else:
        WVR_match = vaddress<top:bottom> == DBGWVR_EL1[n]<top:bottom>;
    return WVR_match and byte_select_match;
# core.IsWatchpointEnabled()
# =====================
# Returns True if the effective value of DBGBCR_EL1[n].E is '1', and False otherwise.
boolean core.IsWatchpointEnabled(integer n)
    if (n > 15 and
            ((not core.HaltOnBreakpointOrWatchpoint() and not core.SelfHostedExtendedBPWPEnabled()) or
            (core.HaltOnBreakpointOrWatchpoint() and EDSCR2.EBWE == '0'))) then
        return False;
    return DBGWCR_EL1[n].E == '1';
# AArch64.core.WatchpointMatch()
# =========================
# Watchpoint matching in an AArch64 translation regime.
boolean AArch64.core.WatchpointMatch(integer n, core.bits(64) vaddress, integer size,
                                AccessDescriptor accdesc)
    assert not core.ELUsingAArch32(core.S1TranslationRegime());
    assert n < core.NumWatchpointsImplemented();
    enabled = core.IsWatchpointEnabled(n);
    linked = DBGWCR_EL1[n].WT == '1';
    isbreakpnt = False;
    ssce = DBGWCR_EL1[n].SSCE if core.HaveRME() else '0';
    state_match = AArch64.core.StateMatch(DBGWCR_EL1[n].SSC, ssce, DBGWCR_EL1[n].HMC, DBGWCR_EL1[n].PAC,
                                     linked, DBGWCR_EL1[n].LBN, isbreakpnt, accdesc);
    ls_match = False;
    case core.Field(DBGWCR_EL1[n].LSC,1,0) of
        when '00' ls_match = False;
        when '01' ls_match = accdesc.read;
        when '10' ls_match = accdesc.write or accdesc.acctype == AccessType_DC;
        when '11' ls_match = True;
    value_match = False;
    for byte = 0 to size - 1
        value_match = value_match or AArch64.core.WatchpointByteMatch(n, vaddress + byte);
    return value_match and state_match and ls_match and enabled;
# core.IsDataAccess()
# ==============
# Return True if access is to data memory.
boolean core.IsDataAccess(AccessType acctype)
    return not (acctype IN {AccessType_IFETCH,
                         AccessType_TTW,
                         AccessType_DC,
                         AccessType_IC,
                         AccessType_AT});
# AArch64.core.CheckWatchpoint()
# =========================
# Called before accessing the memory location of "size" bytes at "address",
# when either debug exceptions are enabled for the access, or halting debug
# is enabled and halting is allowed.
FaultRecord AArch64.core.CheckWatchpoint(FaultRecord fault_in, core.bits(64) vaddress,
                                    AccessDescriptor accdesc, integer size)
    assert not core.ELUsingAArch32(core.S1TranslationRegime());
    FaultRecord fault = fault_in;
    if accdesc.acctype == AccessType_DC:
        if accdesc.cacheop != CacheOp_Invalidate:
            return fault;
    elsif not core.IsDataAccess(accdesc.acctype):
        return fault;
    for i = 0 to core.NumWatchpointsImplemented() - 1
        if AArch64.core.WatchpointMatch(i, vaddress, size, accdesc):
            fault.statuscode = Fault_Debug;
            if DBGWCR_EL1[i]core.Bit(.LSC,0) == '1' and accdesc.read:
                fault.write = False;
            elsif DBGWCR_EL1[i]core.Bit(.LSC,1) == '1' and accdesc.write:
                fault.write = True;
    if (fault.statuscode == Fault_Debug and core.HaltOnBreakpointOrWatchpoint() and
            not accdesc.nonfault and not (accdesc.firstfault and not accdesc.first)) then
        reason = DebugHalt_Watchpoint;
        EDWAR = vaddress;
        core.Halt(reason);
    return fault;
# AArch64.core.GenerateDebugExceptionsFrom()
# =====================================
boolean AArch64.core.GenerateDebugExceptionsFrom(core.bits(2) from_el, SecurityState from_state, bit mask)
    if OSLSR_EL1.OSLK == '1' or core.DoubleLockStatus() or core.Halted():
        return False;
    route_to_el2 = (core.HaveEL(EL2) and (from_state != SS_Secure or core.IsSecureEL2Enabled()) and
                   (HCR_EL2.TGE == '1' or MDCR_EL2.TDE == '1'));
    target = (EL2 if route_to_el2 else EL1);
    enabled = False;
    if core.HaveEL(EL3) and from_state == SS_Secure:
        enabled = MDCR_EL3.SDD == '0';
        if from_el == EL0 and core.ELUsingAArch32(EL1):
            enabled = enabled or SDER32_EL3.SUIDEN == '1';
    else:
        enabled = True;
    if from_el == target:
        enabled = enabled and MDSCR_EL1.KDE == '1' and mask == '0';
    else:
        enabled = enabled and core.UInt(target) > core.UInt(from_el);
    return enabled;
# AArch64.core.GenerateDebugExceptions()
# =================================
boolean AArch64.core.GenerateDebugExceptions()
    ss = core.CurrentSecurityState();
    return AArch64.core.GenerateDebugExceptionsFrom(core.APSR.EL, ss, core.APSR.D);
# core.GPCNoFault()
# ============
# Returns the default properties of a GPCF that does not represent a fault
GPCFRecord core.GPCNoFault()
    GPCFRecord result;
    result.gpf = GPCF_None;
    return result;
# core.NoFault()
# =========
# Return a clear fault record indicating no faults have occured
FaultRecord core.NoFault()
    FaultRecord fault;
    fault.statuscode  = Fault_None;
    fault.access      = AccessDescriptor UNKNOWN;
    fault.secondstage = False;
    fault.s2fs1walk   = False;
    fault.dirtybit    = False;
    fault.overlay     = False;
    fault.toplevel    = False;
    fault.assuredonly = False;
    fault.s1tagnotdata = False;
    fault.tagaccess   = False;
    fault.gpcfs2walk  = False;
    fault.gpcf        = core.GPCNoFault();
    return fault;
# core.NoFault()
# =========
# Return a clear fault record indicating no faults have occured for a specific access
FaultRecord core.NoFault(AccessDescriptor accdesc)
    FaultRecord fault;
    fault.statuscode  = Fault_None;
    fault.access      = accdesc;
    fault.secondstage = False;
    fault.s2fs1walk   = False;
    fault.dirtybit    = False;
    fault.overlay     = False;
    fault.toplevel    = False;
    fault.assuredonly = False;
    fault.s1tagnotdata = False;
    fault.tagaccess   = False;
    fault.write       = not accdesc.read and accdesc.write;
    fault.gpcfs2walk  = False;
    fault.gpcf        = core.GPCNoFault();
    return fault;
# AArch64.core.CheckDebug()
# ====================
# Called on each access to check for a debug exception or entry to Debug state.
FaultRecord AArch64.core.CheckDebug(core.bits(64) vaddress, AccessDescriptor accdesc, integer size)
    FaultRecord fault = core.NoFault(accdesc);
    generate_exception = False;
    boolean d_side = (core.IsDataAccess(accdesc.acctype) or accdesc.acctype == AccessType_DC);
    boolean i_side = (accdesc.acctype == AccessType_IFETCH);
    if accdesc.acctype == AccessType_NV2:
        mask = '0';
        ss = core.CurrentSecurityState();
        generate_exception = (AArch64.core.GenerateDebugExceptionsFrom(EL2, ss, mask) and
                              MDSCR_EL1.MDE == '1');
    else:
        generate_exception = AArch64.core.GenerateDebugExceptions() and MDSCR_EL1.MDE == '1';
    halt = core.HaltOnBreakpointOrWatchpoint();
    if generate_exception or halt:
        if d_side:
            fault = AArch64.core.CheckWatchpoint(fault, vaddress, accdesc, size);
        elsif i_side:
            fault = AArch64.core.CheckBreakpoint(fault, vaddress, accdesc, size);
    return fault;
# AArch64.core.GetVARange()
# ====================
# Determines if the VA that is to be translated lies in LOWER or UPPER address range.
VARange AArch64.core.GetVARange(core.bits(64) va)
    if core.Bit(va,55) == '0':
        return VARange_LOWER;
    else:
        return VARange_UPPER;
# core.HaveSmallTranslationTblExt()
# ============================
# Returns True if Small Translation Table Support is implemented.
boolean core.HaveSmallTranslationTableExt()
    return core.IsFeatureImplemented(FEAT_TTST);
# TGx
# ===
# Translation granules sizes
enumeration TGx {
    TGx_4KB,
    TGx_16KB,
    TGx_64KB
};
# AArch64.core.MaxTxSZ()
# =================
# Retrieve the maximum value of TxSZ indicating minimum input address size for both
# stages of translation
integer AArch64.core.MaxTxSZ(TGx tgx)
    if core.HaveSmallTranslationTableExt():
        case tgx of
            when TGx_4KB   return 48;
            when TGx_16KB  return 48;
            when TGx_64KB  return 47;
    return 39;
# core.BigEndianReverse()
# ==================
core.bits(width) BigEndianReverse (core.bits(width) value)
    assert width IN {8, 16, 32, 64, 128};
    integer half = width DIV 2;
    if width == 8:
         return value;
    return core.BigEndianReverse(value<half-1:0>) : core.BigEndianReverse(value<width-1:half>);
# core.DecodePPS()
# ===========
# Size of region protected by the GPT, in bits.
integer core.DecodePPS()
    case GPCCR_EL3.PPS of
        when '000' return 32;
        when '001' return 36;
        when '010' return 40;
        when '011' return 42;
        when '100' return 44;
        when '101' return 48;
        when '110' return 52;
        otherwise core.Unreachable();
# core.AbovePPS()
# ==========
# Returns True if an address exceeds the range configured in GPCCR_EL3.PPS.
boolean core.AbovePPS(core.bits(56) address)
    pps = core.DecodePPS();
    if pps >= 56:
        return False;
    return not core.IsZero(address<55:pps>);
# core.GPCFault()
# ==========
# Constructs and returns a GPCF
GPCFRecord core.GPCFault(GPCF gpf, integer level)
    GPCFRecord fault;
    fault.gpf   = gpf;
    fault.level = level;
    return fault;
# AArch64.core.PAMax()
# ===============
# Returns the IMPLEMENTATION DEFINED maximum number of bits capable of representing
# physical address for this processor
integer AArch64.core.PAMax()
    return integer IMPLEMENTATION_DEFINED "Maximum Physical Address Size";
# core.GPCRegistersConsistent()
# ========================
# Returns whether the GPT registers are configured correctly.
# This returns false if any fields select a Reserved value.
boolean core.GPCRegistersConsistent()
    # Check for Reserved register values
    if GPCCR_EL3.PPS == '111' or core.DecodePPS() > AArch64.core.PAMax():
        return False;
    if GPCCR_EL3.PGS == '11':
        return False;
    if GPCCR_EL3.SH == '01':
        return False;
    # Inner and Outer Non-cacheable requires Outer Shareable
    if GPCCR_EL3.<ORGN, IRGN> == '0000' and GPCCR_EL3.SH != '10':
        return False;
    return True;
constant core.bits(4) GPT_NoAccess  = '0000';
constant core.bits(4) GPT_Table     = '0011';
constant core.bits(4) GPT_Block     = '0001';
constant core.bits(4) GPT_Contig    = '0001';
constant core.bits(4) GPT_Secure    = '1000';
constant core.bits(4) GPT_NonSecure = '1001';
constant core.bits(4) GPT_Root      = '1010';
constant core.bits(4) GPT_Realm     = '1011';
constant core.bits(4) GPT_Any       = '1111';
constant integer GPTRange_4KB   = 12;
constant integer GPTRange_16KB  = 14;
constant integer GPTRange_64KB  = 16;
constant integer GPTRange_2MB   = 21;
constant integer GPTRange_32MB  = 25;
constant integer GPTRange_512MB = 29;
constant integer GPTRange_1GB   = 30;
constant integer GPTRange_16GB  = 34;
constant integer GPTRange_64GB  = 36;
constant integer GPTRange_512GB = 39;
type GPTTable is (
    core.bits(56) address        # Base address of next table
)
type GPTEntry is (
    core.bits(4)  gpi,           # GPI value for this region
    integer  size,          # Region size
    integer  contig_size,   # Contiguous region size
    integer  level,         # Level of GPT lookup
    core.bits(56) pa             # PA uniquely identifying the GPT entry
)
# core.GPICheck()
# ==========
# Returns whether an access to a given physical address space is permitted
# given the configured GPI value.
# paspace: Physical address space of the access
# gpi: Value read from GPT for the access
boolean core.GPICheck(PASpace paspace, core.bits(4) gpi)
    case gpi of
        when GPT_NoAccess  return False;
        when GPT_Secure    assert core.HaveSecureEL2Ext();return paspace == PAS_Secure;
        when GPT_NonSecure return paspace == PAS_NonSecure;
        when GPT_Root      return paspace == PAS_Root;
        when GPT_Realm     return paspace == PAS_Realm;
        when GPT_Any       return True;
        otherwise          core.Unreachable();
# core.CreateAccDescGPTW()
# ===================
# Access descriptor for Granule Protection Table walks
AccessDescriptor core.CreateAccDescGPTW(AccessDescriptor accdesc_in)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_GPTW);
    accdesc.el              = accdesc_in.el;
    accdesc.ss              = accdesc_in.ss;
    accdesc.read            = True;
    accdesc.mpam            = accdesc_in.mpam;
    return accdesc;
# core.GPIValid()
# ==========
# Returns whether a given value is a valid encoding for a GPI value
boolean core.GPIValid(core.bits(4) gpi)
    if gpi == GPT_Secure:
        return core.HaveSecureEL2Ext();
    return gpi IN {GPT_NoAccess,
                   GPT_NonSecure,
                   GPT_Root,
                   GPT_Realm,
                   GPT_Any};
# core.GPTL0Size()
# ===========
# Returns number of bits covered by a level 0 GPT entry
integer core.GPTL0Size()
    case GPCCR_EL3.L0GPTSZ of
        when '0000' return GPTRange_1GB;
        when '0100' return GPTRange_16GB;
        when '0110' return GPTRange_64GB;
        when '1001' return GPTRange_512GB;
        otherwise core.Unreachable();
    return 30;
# PGS
# ===
# Physical granule size
enumeration PGSe {
    PGS_4KB,
    PGS_16KB,
    PGS_64KB
};
# core.DecodeGPTBlock()
# ================
# Validate and decode a GPT Block descriptor
(GPCF, GPTEntry) core.DecodeGPTBlock(PGSe pgs, core.bits(64) entry)
    assert core.Field(entry,3,0) == GPT_Block;
    GPTEntry result;
    if not core.IsZero(core.Field(entry,63,8)):
        return (GPCF_Walk, GPTEntry UNKNOWN);
    if not core.GPIValid(core.Field(entry,7,4)):
        return (GPCF_Walk, GPTEntry UNKNOWN);
    result.gpi   = core.Field(entry,7,4);
    result.level = 0;
    # GPT information from a level 0 GPT Block descriptor is permitted
    # to be cached in a TLB as though the Block is a contiguous region
    # of granules each of the size configured in GPCCR_EL3.PGS.
    case pgs of
        when PGS_4KB  result.size = GPTRange_4KB;
        when PGS_16KB result.size = GPTRange_16KB;
        when PGS_64KB result.size = GPTRange_64KB;
        otherwise core.Unreachable();
    result.contig_size = core.GPTL0Size();
    return (GPCF_None, result);
# core.DecodeGPTContiguous()
# =====================
# Validate and decode a GPT Contiguous descriptor
(GPCF, GPTEntry) core.DecodeGPTContiguous(PGSe pgs, core.bits(64) entry)
    assert core.Field(entry,3,0) == GPT_Contig;
    GPTEntry result;
    if not core.IsZero(core.Field(entry,63,10)):
        return (GPCF_Walk, result);
    result.gpi = core.Field(entry,7,4);
    if not core.GPIValid(result.gpi):
        return (GPCF_Walk, result);
    case pgs of
        when PGS_4KB  result.size = GPTRange_4KB;
        when PGS_16KB result.size = GPTRange_16KB;
        when PGS_64KB result.size = GPTRange_64KB;
        otherwise core.Unreachable();
    case core.Field(entry,9,8) of
        when '01' result.contig_size = GPTRange_2MB;
        when '10' result.contig_size = GPTRange_32MB;
        when '11' result.contig_size = GPTRange_512MB;
        otherwise return (GPCF_Walk, GPTEntry UNKNOWN);
    result.level = 1;
    return (GPCF_None, result);
# core.DecodeGPTGranules()
# ===================
# Validate and decode a GPT Granules descriptor
(GPCF, GPTEntry) core.DecodeGPTGranules(PGSe pgs, integer index, core.bits(64) entry)
    GPTEntry result;
    for i in range(0,15+1):
        if not core.GPIValid(entry<i*4 +:4>):
            return (GPCF_Walk, result);
    result.gpi = entry<index*4 +:4>;
    case pgs of
        when PGS_4KB  result.size = GPTRange_4KB;
        when PGS_16KB result.size = GPTRange_16KB;
        when PGS_64KB result.size = GPTRange_64KB;
        otherwise core.Unreachable();
    result.contig_size = result.size; # No contiguity
    result.level = 1;
    return (GPCF_None, result);
# core.DecodeGPTTable()
# ================
# Validate and decode a GPT Table descriptor
(GPCF, GPTTable) core.DecodeGPTTable(PGSe pgs, core.bits(64) entry)
    assert core.Field(entry,3,0) == GPT_Table;
    GPTTable result;
    if not core.IsZero(entry<63:52,11:4>):
        return (GPCF_Walk, GPTTable UNKNOWN);
    l0sz = core.GPTL0Size();
    p = 0;
    case pgs of
        when PGS_4KB  p = 12;
        when PGS_16KB p = 14;
        when PGS_64KB p = 16;
        otherwise core.Unreachable();
    if not core.IsZero(entry<(l0sz-p)-2:12>):
        return (GPCF_Walk, GPTTable UNKNOWN);
    case pgs of
        when PGS_4KB  result.address = core.Field(entry,55,17):core.Zeros(17);
        when PGS_16KB result.address = core.Field(entry,55,15):core.Zeros(15);
        when PGS_64KB result.address = core.Field(entry,55,13):core.Zeros(13);
        otherwise core.Unreachable();
    # The address must be within the range covered by the GPT
    if core.AbovePPS(result.address):
        return (GPCF_AddressSize, GPTTable UNKNOWN);
    return (GPCF_None, result);
# core.DecodePGS()
# ===========
PGSe core.DecodePGS(core.bits(2) pgs)
    case pgs of
        when '00' return PGS_4KB;
        when '10' return PGS_16KB;
        when '01' return PGS_64KB;
        otherwise core.Unreachable();
# core.GPIIndex()
# ==========
integer core.GPIIndex(core.bits(56) pa)
    case core.DecodePGS(GPCCR_EL3.PGS) of
        when PGS_4KB  return core.UInt(core.Field(pa,15,12));
        when PGS_16KB return core.UInt(core.Field(pa,17,14));
        when PGS_64KB return core.UInt(core.Field(pa,19,16));
        otherwise core.Unreachable();
# core.GPTLevel0Index()
# ================
# Compute the level 0 index based on input PA.
integer core.GPTLevel0Index(core.bits(56) pa)
    # Input address and index bounds
    pps = core.DecodePPS();
    l0sz = core.GPTL0Size();
    if pps <= l0sz:
        return 0;
    return core.UInt(pa<pps-1:l0sz>);
# core.GPTLevel1Index()
# ================
# Compute the level 1 index based on input PA.
integer core.GPTLevel1Index(core.bits(56) pa)
    # Input address and index bounds
    l0sz = core.GPTL0Size();
    case core.DecodePGS(GPCCR_EL3.PGS) of
        when PGS_4KB  return core.UInt(pa<l0sz-1:16>);
        when PGS_16KB return core.UInt(pa<l0sz-1:18>);
        when PGS_64KB return core.UInt(pa<l0sz-1:20>);
        otherwise core.Unreachable();
# PhysMemRetStatus
# ================
# Fields that relate only to return values of PhysMem functions.
type PhysMemRetStatus is (
    Fault       statuscode,     # Fault Status
    bit         extflag,        # IMPLEMENTATION DEFINED syndrome for External aborts
    ErrorState  merrorstate,    # Optional error state returned on a physical memory access
    core.bits(64)    store64bstatus  # Status of 64B store
)
# core.IsFault()
# =========
# Return True if a fault is associated with an address descriptor
boolean core.IsFault(AddressDescriptor addrdesc)
    return addrdesc.fault.statuscode != Fault_None;
# core.IsFault()
# =========
# Return True if a fault is associated with a memory access.
boolean core.IsFault(Fault fault)
    return fault != Fault_None;
# core.IsFault()
# =========
# Return True if a fault is associated with status returned by memory.
boolean core.IsFault(PhysMemRetStatus retstatus)
    return retstatus.statuscode != Fault_None;
# core.Max()
# =====
integer core.Max(integer a, integer b)
    return a if a >= b else b;
# core.Max()
# =====
real core.Max(real a, real b)
    return a if a >= b else b;
# core.PhysMemRead()
# =============
# Returns the value read from memory, and a status.
# Returned value is UNKNOWN if an External abort occurred while reading the
# memory.
# Otherwise the PhysMemRetStatus statuscode is Fault_None.
(PhysMemRetStatus, core.bits(8*size)) core.PhysMemRead(AddressDescriptor desc, integer size,
                                             AccessDescriptor accdesc);
constant core.bits(2) MemAttr_NC = '00';     # Non-cacheable
constant core.bits(2) MemAttr_WT = '10';     # Write-through
constant core.bits(2) MemAttr_WB = '11';     # Write-back
constant core.bits(2) MemHint_No = '00';     # No Read-Allocate, No Write-Allocate
constant core.bits(2) MemHint_WA = '01';     # No Read-Allocate, Write-Allocate
constant core.bits(2) MemHint_RA = '10';     # Read-Allocate, No Write-Allocate
constant core.bits(2) MemHint_RWA = '11';    # Read-Allocate, Write-Allocate
# core.DecodeSDFAttr()
# ===============
# Decode memory attributes using SDF (Short Descriptor Format) mapping
MemAttrHints core.DecodeSDFAttr(core.bits(2) rgn)
    MemAttrHints sdfattr;
    case rgn of
        when '00'                   # Non-cacheable (no allocate)
            sdfattr.attrs = MemAttr_NC;
        when '01'                   # Write-back, Read and Write allocate
            sdfattr.attrs = MemAttr_WB;
            sdfattr.hints = MemHint_RWA;
        when '10'                   # Write-through, Read allocate
            sdfattr.attrs = MemAttr_WT;
            sdfattr.hints = MemHint_RA;
        when '11'                   # Write-back, Read allocate
            sdfattr.attrs = MemAttr_WB;
            sdfattr.hints = MemHint_RA;
    sdfattr.transient = False;
    return sdfattr;
# core.ConstrainUnpredictable()
# ========================
# Return the appropriate Constraint result to control the caller's behavior.
# The return value is IMPLEMENTATION DEFINED within a permitted list for each
# raise Exception('UNPREDICTABLE') case.
# (The permitted list is determined by an assert or case statement at the call site.)
Constraint core.ConstrainUnpredictable(Unpredictable which);
# core.DecodeShareability()
# ====================
# Decode shareability of target memory region
Shareability core.DecodeShareability(core.bits(2) sh)
    case sh of
        when '10' return Shareability_OSH;
        when '11' return Shareability_ISH;
        when '00' return Shareability_NSH;
        otherwise
            case core.ConstrainUnpredictable(Unpredictable_Shareability) of
                when Constraint_OSH return Shareability_OSH;
                when Constraint_ISH return Shareability_ISH;
                when Constraint_NSH return Shareability_NSH;
# core.WalkMemAttrs()
# ==============
# Retrieve memory attributes of translation table walk
MemoryAttributes core.WalkMemAttrs(core.bits(2) sh, core.bits(2) irgn, core.bits(2) orgn)
    MemoryAttributes walkmemattrs;
    walkmemattrs.memtype      = MemType_Normal;
    walkmemattrs.shareability = core.DecodeShareability(sh);
    walkmemattrs.inner        = core.DecodeSDFAttr(irgn);
    walkmemattrs.outer        = core.DecodeSDFAttr(orgn);
    walkmemattrs.tags         = MemTag_Untagged;
    if (walkmemattrs.inner.attrs == MemAttr_WB and
            walkmemattrs.outer.attrs == MemAttr_WB) then
        walkmemattrs.xs = '0';
    else:
        walkmemattrs.xs = '1';
    walkmemattrs.notagaccess = False;
    return walkmemattrs;
# core.GPTWalk()
# =========
# Get the GPT entry for a given physical address, pa
(GPCFRecord, GPTEntry) core.GPTWalk(core.bits(56) pa, AccessDescriptor accdesc)
    # GPT base address
    base = 0;
    pgs = core.DecodePGS(GPCCR_EL3.PGS);
    # The level 0 GPT base address is aligned to the greater of:
    # * the size of the level 0 GPT, determined by GPCCR_EL3.{PPS, L0GPTSZ}.
    # * 4KB
    base = core.ZeroExtend(GPTBR_EL3.BADDR:core.Zeros(12), 56);
    pps = core.DecodePPS();
    l0sz = core.GPTL0Size();
    integer alignment = core.Max((pps - l0sz) + 3, 12);
    base = base & NOT core.ZeroExtend(core.Ones(alignment), 56);
    AccessDescriptor gptaccdesc = core.CreateAccDescGPTW(accdesc);
    # Access attributes and address for GPT fetches
    AddressDescriptor gptaddrdesc;
    gptaddrdesc.memattrs = core.WalkMemAttrs(GPCCR_EL3.SH, GPCCR_EL3.ORGN, GPCCR_EL3.IRGN);
    gptaddrdesc.fault    = core.NoFault(gptaccdesc);
    # Address of level 0 GPT entry
    gptaddrdesc.paddress.paspace = PAS_Root;
    gptaddrdesc.paddress.address = base + core.GPTLevel0Index(pa) * 8;
    # Fetch L0GPT entry
    level_0_entry = 0;
    PhysMemRetStatus memstatus;
    (memstatus, level_0_entry) = core.PhysMemRead(gptaddrdesc, 8, gptaccdesc);
    if core.IsFault(memstatus):
        return (core.GPCFault(GPCF_EABT, 0), GPTEntry UNKNOWN);
    GPTEntry result;
    GPTTable table;
    GPCF gpf;
    case core.Field(level_0_entry,3,0) of
        when GPT_Block
            # Decode the GPI value and return that
            (gpf, result) = core.DecodeGPTBlock(pgs, level_0_entry);
            result.pa = pa;
            return (core.GPCFault(gpf, 0), result);
        when GPT_Table
            # Decode the table entry and continue walking
            (gpf, table) = core.DecodeGPTTable(pgs, level_0_entry);
            if gpf != GPCF_None:
                return (core.GPCFault(gpf, 0), GPTEntry UNKNOWN);
        otherwise
            # GPF - invalid encoding
            return (core.GPCFault(GPCF_Walk, 0), GPTEntry UNKNOWN);
    # Must be a GPT Table entry
    assert core.Field(level_0_entry,3,0) == GPT_Table;
    # Address of level 1 GPT entry
    offset = core.GPTLevel1Index(pa) * 8;
    gptaddrdesc.paddress.address = table.address + offset;
    # Fetch L1GPT entry
    level_1_entry = 0;
    (memstatus, level_1_entry) = core.PhysMemRead(gptaddrdesc, 8, gptaccdesc);
    if core.IsFault(memstatus):
        return (core.GPCFault(GPCF_EABT, 1), GPTEntry UNKNOWN);
    case core.Field(level_1_entry,3,0) of
        when GPT_Contig
            (gpf, result) = core.DecodeGPTContiguous(pgs, level_1_entry);
        otherwise
            gpi_index = core.GPIIndex(pa);
            (gpf, result) = core.DecodeGPTGranules(pgs, gpi_index, level_1_entry);
    if gpf != GPCF_None:
        return (core.GPCFault(gpf, 1), GPTEntry UNKNOWN);
    result.pa = pa;
    return (core.GPCNoFault(), result);
# core.GranuleProtectionCheck()
# ========================
# Returns whether a given access is permitted, according to the
# granule protection check.
# addrdesc and accdesc describe the access to be checked.
GPCFRecord core.GranuleProtectionCheck(AddressDescriptor addrdesc, AccessDescriptor accdesc)
    assert core.HaveRME();
    # The address to be checked
    address = addrdesc.paddress;
    # Bypass mode - all accesses pass
    if GPCCR_EL3.GPC == '0':
        return core.GPCNoFault();
    # Configuration consistency check
    if not core.GPCRegistersConsistent():
        return core.GPCFault(GPCF_Walk, 0);
    # Input address size check
    if core.AbovePPS(address.address):
        if address.paspace == PAS_NonSecure:
            return core.GPCNoFault();
        else:
            return core.GPCFault(GPCF_Fail, 0);
    # GPT base address size check
    core.bits(56) gpt_base = core.ZeroExtend(GPTBR_EL3.BADDR:core.Zeros(12), 56);
    if core.AbovePPS(gpt_base):
        return core.GPCFault(GPCF_AddressSize, 0);
    # GPT lookup
    (gpcf, gpt_entry) = core.GPTWalk(address.address, accdesc);
    if gpcf.gpf != GPCF_None:
        return gpcf;
    # Check input physical address space against GPI
    permitted = core.GPICheck(address.paspace, gpt_entry.gpi);
    if not permitted:
        gpcf = core.GPCFault(GPCF_Fail, gpt_entry.level);
        return gpcf;
    # Check passed
    return core.GPCNoFault();
# core.HaveRASExt()
# ============
boolean core.HaveRASExt()
    return core.IsFeatureImplemented(FEAT_RAS);
# core.IsExternalAbortTakenSynchronously()
# ===================================
# Return an implementation specific value:
# True if the fault returned for the access can be taken synchronously,
# False otherwise.
#
# This might vary between accesses, for example depending on the error type1
# or memory type1 being accessed.
# External aborts on data accesses and translation table walks on data accesses
# can be either synchronous or asynchronous.
#
# When FEAT_DoubleFault is not implemented, External aborts on instruction
# fetches and translation table walks on instruction fetches can be either
# synchronous or asynchronous.
# When FEAT_DoubleFault is implemented, all External abort exceptions on
# instruction fetches and translation table walks on instruction fetches
# must be synchronous.
boolean core.IsExternalAbortTakenSynchronously(PhysMemRetStatus memstatus,
                                          boolean iswrite,
                                          AddressDescriptor desc,
                                          integer size,
                                          AccessDescriptor accdesc);
# core.IsExternalSyncAbort()
# =====================
# Returns True if the abort currently being processed is an external
# synchronous abort and False otherwise.
boolean core.IsExternalSyncAbort(Fault statuscode)
    assert statuscode != Fault_None;
    return (statuscode IN {
        Fault_SyncExternal,
        Fault_SyncParity,
        Fault_SyncExternalOnWalk,
        Fault_SyncParityOnWalk
    });
# core.IsExternalSyncAbort()
# =====================
boolean core.IsExternalSyncAbort(FaultRecord fault)
    return core.IsExternalSyncAbort(fault.statuscode) or fault.gpcf.gpf == GPCF_EABT;
# core.PendSErrorInterrupt()
# =====================
# Pend the SError Interrupt.
core.PendSErrorInterrupt(FaultRecord fault);
# core.HandleExternalTTWAbort()
# ========================
# Take Asynchronous abort or update FaultRecord for Translation Table Walk
# based on PhysMemRetStatus.
FaultRecord core.HandleExternalTTWAbort(PhysMemRetStatus memretstatus, boolean iswrite,
                                   AddressDescriptor memaddrdesc,
                                   AccessDescriptor accdesc, integer size,
                                   FaultRecord input_fault)
    output_fault = input_fault;
    output_fault.extflag = memretstatus.extflag;
    output_fault.statuscode = memretstatus.statuscode;
    if (core.IsExternalSyncAbort(output_fault) and
            not core.IsExternalAbortTakenSynchronously(memretstatus, iswrite, memaddrdesc,
                                               size, accdesc)) then
        if output_fault.statuscode == Fault_SyncParity:
            output_fault.statuscode = Fault_AsyncParity;
        else:
            output_fault.statuscode = Fault_AsyncExternal;
    # If a synchronous fault is on a translation table walk, then update
    # the fault type1
    if core.IsExternalSyncAbort(output_fault):
        if output_fault.statuscode == Fault_SyncParity:
            output_fault.statuscode = Fault_SyncParityOnWalk;
        else:
            output_fault.statuscode = Fault_SyncExternalOnWalk;
    if core.HaveRASExt():
        output_fault.merrorstate = memretstatus.merrorstate;
    if not core.IsExternalSyncAbort(output_fault):
        core.PendSErrorInterrupt(output_fault);
        output_fault.statuscode = Fault_None;
    return output_fault;
# core.PhysMemWrite()
# ==============
# Writes the value to memory, and returns the status of the write.
# If there is an External abort on the write, the PhysMemRetStatus indicates this.
# Otherwise the statuscode of PhysMemRetStatus is Fault_None.
PhysMemRetStatus core.PhysMemWrite(AddressDescriptor desc, integer size, AccessDescriptor accdesc,
                              core.bits(8*size) value);
# AArch64.core.MemSwapTableDesc()
# ==========================
# Perform HW update of table descriptor as an atomic operation
(FaultRecord, core.bits(N)) AArch64.core.MemSwapTableDesc(FaultRecord fault_in, core.bits(N) prev_desc,
                                                core.bits(N) new_desc, bit ee,
                                                AccessDescriptor  descaccess,
                                                AddressDescriptor descpaddr)
    FaultRecord fault = fault_in;
    iswrite = False;
    if core.HaveRME():
        fault.gpcf = core.GranuleProtectionCheck(descpaddr, descaccess);
        if fault.gpcf.gpf != GPCF_None:
            fault.statuscode = Fault_GPCFOnWalk;
            fault.paddress   = descpaddr.paddress;
            fault.gpcfs2walk = fault.secondstage;
            return (fault, core.bits(N) UNKNOWN);
    # All observers in the shareability domain observe the
    # following memory read and write accesses atomically.
    core.bits(N) mem_desc;
    PhysMemRetStatus memstatus;
    (memstatus, mem_desc) = core.PhysMemRead(descpaddr, N DIV 8, descaccess);
    if ee == '1':
        mem_desc = core.BigEndianReverse(mem_desc);
    if core.IsFault(memstatus):
        iswrite = False;
        fault = core.HandleExternalTTWAbort(memstatus, iswrite, descpaddr, descaccess, N DIV 8, fault);
        if core.IsFault(fault.statuscode):
            return (fault, core.bits(N) UNKNOWN);
    if mem_desc == prev_desc :
        ordered_new_desc = core.BigEndianReverse(new_desc) if ee == '1' else new_desc;
        memstatus = core.PhysMemWrite(descpaddr, N DIV 8, descaccess, ordered_new_desc);
        if core.IsFault(memstatus):
            iswrite = True;
            fault = core.HandleExternalTTWAbort(memstatus, iswrite, descpaddr, descaccess, N DIV 8,
                                           fault);
            if core.IsFault(fault.statuscode):
                return (fault, core.bits(N) UNKNOWN);
        # Reflect what is now in memory (in little endian format)
        mem_desc = new_desc;
    return (fault, mem_desc);
# Regime
# ======
# Translation regimes
enumeration Regime {
    Regime_EL3,            # EL3
    Regime_EL30,           # EL3&0 (PL1&0 when EL3 is AArch32)
    Regime_EL2,            # EL2
    Regime_EL20,           # EL2&0
    Regime_EL10            # EL1&0
};
# AArch64.core.S1DCacheEnabled()
# =========================
# Determine cacheability of stage 1 data accesses
boolean AArch64.core.S1DCacheEnabled(Regime regime)
    case regime of
        when Regime_EL3  return SCTLR_EL3.C == '1';
        when Regime_EL2  return SCTLR_EL2.C == '1';
        when Regime_EL20 return SCTLR_EL2.C == '1';
        when Regime_EL10 return SCTLR_EL1.C == '1';
# AArch64.core.AddrTop()
# =================
# Get the top bit position of the virtual address.
# Bits above are not accounted as part of the translation process.
integer AArch64.core.AddrTop(bit tbid, AccessType acctype, bit tbi)
    if tbid == '1' and acctype == AccessType_IFETCH:
        return 63;
    if tbi == '1':
        return 55;
    else:
        return 63;
# AArch64.core.S1HasAlignmentFault()
# =============================
# Returns whether stage 1 output fails alignment requirement on data accesses
# to Device memory
boolean AArch64.core.S1HasAlignmentFault(AccessDescriptor accdesc, boolean aligned,
                                    bit ntlsmd, MemoryAttributes memattrs)
    if accdesc.acctype == AccessType_IFETCH:
        return False;
    elsif core.HaveMTEExt() and accdesc.tagaccess and accdesc.write:
        return (memattrs.memtype == MemType_Device and
                core.ConstrainUnpredictable(Unpredictable_DEVICETAGSTORE) == Constraint_FAULT);
    elsif accdesc.a32lsmd and ntlsmd == '0':
        return memattrs.memtype == MemType_Device and  memattrs.device != DeviceType_GRE;
    elsif accdesc.acctype == AccessType_DCZero:
        return memattrs.memtype == MemType_Device;
    else:
        return memattrs.memtype == MemType_Device and not aligned;
# AArch64.core.S1ICacheEnabled()
# =========================
# Determine cacheability of stage 1 instruction fetches
boolean AArch64.core.S1ICacheEnabled(Regime regime)
    case regime of
        when Regime_EL3  return SCTLR_EL3.I == '1';
        when Regime_EL2  return SCTLR_EL2.I == '1';
        when Regime_EL20 return SCTLR_EL2.I == '1';
        when Regime_EL10 return SCTLR_EL1.I == '1';
# core.CreateAddressDescriptor()
# =========================
# Set internal members for address descriptor type1 to valid values
AddressDescriptor core.CreateAddressDescriptor(core.bits(64) va, FullAddress pa,
                                          MemoryAttributes memattrs)
    AddressDescriptor addrdesc;
    addrdesc.paddress = pa;
    addrdesc.vaddress = va;
    addrdesc.memattrs = memattrs;
    addrdesc.fault    = core.NoFault();
    addrdesc.s1assured = False;
    return addrdesc;
# core.HasUnprivileged()
# =================
# Returns whether a translation regime serves EL0 as well as a higher EL
boolean core.HasUnprivileged(Regime regime)
    return (regime IN {
        Regime_EL20,
        Regime_EL30,
        Regime_EL10
    });
InGuardedPage = False;
# core.SetInGuardedPage()
# ==================
# Global state updated to denote if memory access is from a guarded page.
core.SetInGuardedPage(boolean guardedpage)
    InGuardedPage = guardedpage;
# AArch64.core.S1DisabledOutput()
# ==========================
# Map the VA to IPA/PA and assign default memory attributes
(FaultRecord, AddressDescriptor) AArch64.core.S1DisabledOutput(FaultRecord fault_in, Regime regime,
                                                          core.bits(64) va_in, AccessDescriptor accdesc,
                                                          boolean aligned)
    core.bits(64) va = va_in;
    walkparams = AArch64.core.GetS1TTWParams(regime, accdesc.ss, va);
    FaultRecord fault = fault_in;
    # No memory page is guarded when stage 1 address translation is disabled
    core.SetInGuardedPage(False);
    # Output Address
    FullAddress oa;
    oa.address = core.Field(va,55,0);
    case accdesc.ss of
        when SS_Secure    oa.paspace = PAS_Secure;
        when SS_NonSecure oa.paspace = PAS_NonSecure;
        when SS_Root      oa.paspace = PAS_Root;
        when SS_Realm     oa.paspace = PAS_Realm;
    MemoryAttributes memattrs;
    if regime == Regime_EL10 and core.EL2Enabled() and walkparams.dc == '1':
        MemAttrHints default_cacheability;
        default_cacheability.attrs     = MemAttr_WB;
        default_cacheability.hints     = MemHint_RWA;
        default_cacheability.transient = False;
        memattrs.memtype      = MemType_Normal;
        memattrs.outer        = default_cacheability;
        memattrs.inner        = default_cacheability;
        memattrs.shareability = Shareability_NSH;
        if walkparams.dct == '1':
            memattrs.tags     = MemTag_AllocationTagged;
        elsif walkparams.mtx == '1':
            memattrs.tags     = MemTag_CanonicallyTagged;
            if walkparams.tbi == '0':
                # For the purpose of the checks in this function, the MTE tag bits are ignored.
                va = core.SetField(va,59,56,core.Replicate(core.Bit(va,55), 4));
        else:
            memattrs.tags     = MemTag_Untagged;
        memattrs.xs           = '0';
    elsif accdesc.acctype == AccessType_IFETCH:
        MemAttrHints i_cache_attr;
        if AArch64.core.S1ICacheEnabled(regime):
            i_cache_attr.attrs     = MemAttr_WT;
            i_cache_attr.hints     = MemHint_RA;
            i_cache_attr.transient = False;
        else:
            i_cache_attr.attrs     = MemAttr_NC;
        memattrs.memtype      = MemType_Normal;
        memattrs.outer        = i_cache_attr;
        memattrs.inner        = i_cache_attr;
        memattrs.shareability = Shareability_OSH;
        if walkparams.mtx == '1':
            memattrs.tags     = MemTag_CanonicallyTagged;
        else:
            memattrs.tags     = MemTag_Untagged;
        memattrs.xs           = '1';
    else:
        memattrs.memtype      = MemType_Device;
        memattrs.device       = DeviceType_nGnRnE;
        memattrs.shareability = Shareability_OSH;
        if walkparams.mtx == '1':
            memattrs.tags = MemTag_CanonicallyTagged;
            if walkparams.tbi == '0':
                # For the purpose of the checks in this function, the MTE tag bits are ignored.
                if core.HasUnprivileged(regime):
                    va = core.SetField(va,59,56,core.Replicate(core.Bit(va,55), 4));
                else:
                    va = core.SetField(va,59,56,'0000');
        else:
            memattrs.tags = MemTag_Untagged;
        memattrs.xs           = '1';
    memattrs.notagaccess = False;
    fault.level = 0;
    addrtop     = AArch64.core.AddrTop(walkparams.tbid, accdesc.acctype, walkparams.tbi);
    if not core.IsZero(va<addrtop:AArch64.core.PAMax()>):
        fault.statuscode = Fault_AddressSize;
    elsif AArch64.core.S1HasAlignmentFault(accdesc, aligned, walkparams.ntlsmd, memattrs):
        fault.statuscode = Fault_Alignment;
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN);
    else:
        ipa = core.CreateAddressDescriptor(va_in, oa, memattrs);
        ipa.mecid = AArch64.core.S1DisabledOutputMECID(walkparams, regime, ipa.paddress.paspace);
        return (fault, ipa);
# AArch64.core.S1Enabled()
# ===================
# Determine if stage 1 is enabled for the access type1 for this translation regime
boolean AArch64.core.S1Enabled(Regime regime, AccessType acctype)
    case regime of
        when Regime_EL3  return SCTLR_EL3.M == '1';
        when Regime_EL2  return SCTLR_EL2.M == '1';
        when Regime_EL20 return SCTLR_EL2.M == '1';
        when Regime_EL10 return (not core.EL2Enabled() or HCR_EL2.<DC,TGE> == '00') and SCTLR_EL1.M == '1';
# AArch64.core.S1MinTxSZ()
# ===================
# Retrieve the minimum value of TxSZ indicating maximum input address size for stage 1
integer AArch64.core.S1MinTxSZ(Regime regime, bit d128, bit ds, TGx tgx)
    if core.Have56BitVAExt() and d128 == '1':
        if core.HasUnprivileged(regime):
            return 9;
        else:
            return 8;
    if (core.Have52BitVAExt() and tgx == TGx_64KB) or ds == '1':
        return 12;
    return 16;
# AArch64.core.S2HasAlignmentFault()
# =============================
# Returns whether stage 2 output fails alignment requirement on data accesses
# to Device memory
boolean AArch64.core.S2HasAlignmentFault(AccessDescriptor accdesc, boolean aligned,
                                    MemoryAttributes memattrs)
    if accdesc.acctype == AccessType_IFETCH:
        return False;
    elsif core.HaveMTEExt() and accdesc.tagaccess and accdesc.write:
        return (memattrs.memtype == MemType_Device and
                core.ConstrainUnpredictable(Unpredictable_DEVICETAGSTORE) == Constraint_FAULT);
    elsif accdesc.acctype == AccessType_DCZero:
        return memattrs.memtype == MemType_Device;
    else:
        return memattrs.memtype == MemType_Device and not aligned;
# core.Have52BitPAExt()
# ================
# Returns True if Large Physical Address extension
# support is implemented and False otherwise.
boolean core.Have52BitPAExt()
    return core.IsFeatureImplemented(FEAT_LPA);
# AArch64.core.S2MinTxSZ()
# ===================
# Retrieve the minimum value of TxSZ indicating maximum input address size for stage 2
integer AArch64.core.S2MinTxSZ(bit d128, bit ds, TGx tgx, boolean s1aarch64)
    ips = AArch64.core.PAMax();
    if d128 == '0':
        if core.Have52BitPAExt() and tgx != TGx_64KB and ds == '0':
            ips = core.Min(48, AArch64.core.PAMax());
        else:
            ips = core.Min(52, AArch64.core.PAMax());
    min_txsz = 64 - ips;
    if not s1aarch64:
        # EL1 is AArch32
        min_txsz = core.Min(min_txsz, 24);
    return min_txsz;
# AArch64.core.SettingAccessFlagPermitted()
# ====================================
# Determine whether the access flag could be set by HW given the fault status
boolean AArch64.core.SettingAccessFlagPermitted(FaultRecord fault)
    if fault.statuscode == Fault_None:
        return True;
    elsif fault.statuscode IN {Fault_Alignment, Fault_Permission}:
        return core.ConstrainUnpredictableBool(Unpredictable_AFUPDATE);
    else:
        return False;
# AArch64.core.SettingDirtyStatePermitted()
# ====================================
# Determine whether the dirty state could be set by HW given the fault status
boolean AArch64.core.SettingDirtyStatePermitted(FaultRecord fault)
    if fault.statuscode == Fault_None:
        return True;
    elsif fault.statuscode == Fault_Alignment:
        return core.ConstrainUnpredictableBool(Unpredictable_DBUPDATE);
    else:
        return False;
# core.CreateAccDescTTEUpdate()
# ========================
# Access descriptor for translation table entry HW update
AccessDescriptor core.CreateAccDescTTEUpdate(AccessDescriptor accdesc_in)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_TTW);
    accdesc.el              = accdesc_in.el;
    accdesc.ss              = accdesc_in.ss;
    accdesc.atomicop        = True;
    accdesc.modop           = MemAtomicOp_CAS;
    accdesc.read            = True;
    accdesc.write           = True;
    accdesc.mpam            = accdesc_in.mpam;
    return accdesc;
# core.NormalNCMemAttr()
# =================
# Normal Non-cacheable memory attributes
MemoryAttributes core.NormalNCMemAttr()
    MemAttrHints non_cacheable;
    non_cacheable.attrs = MemAttr_NC;
    MemoryAttributes nc_memattrs;
    nc_memattrs.memtype      = MemType_Normal;
    nc_memattrs.outer        = non_cacheable;
    nc_memattrs.inner        = non_cacheable;
    nc_memattrs.shareability = Shareability_OSH;
    nc_memattrs.tags         = MemTag_Untagged;
    nc_memattrs.notagaccess  = False;
    return nc_memattrs;
# core.EffectiveShareability()
# =======================
# Force Outer Shareability on Device and Normal iNCoNC memory
Shareability core.EffectiveShareability(MemoryAttributes memattrs)
    if (memattrs.memtype == MemType_Device or
            (memattrs.inner.attrs == MemAttr_NC and
             memattrs.outer.attrs == MemAttr_NC)) then
        return Shareability_OSH;
    else:
        return memattrs.shareability;
# core.HaveMTEPermExt()
# ================
# Returns True if MTE_PERM implemented, and False otherwise.
boolean core.HaveMTEPermExt()
    return core.IsFeatureImplemented(FEAT_MTE_PERM);
# core.S2CombineS1AttrHints()
# ======================
# Determine resultant Normal memory cacheability and allocation hints from
# combining stage 1 Normal memory attributes and stage 2 cacheability attributes.
MemAttrHints core.S2CombineS1AttrHints(MemAttrHints s1_attrhints, MemAttrHints s2_attrhints)
    MemAttrHints attrhints;
    if s1_attrhints.attrs == MemAttr_NC or s2_attrhints.attrs == MemAttr_NC:
        attrhints.attrs = MemAttr_NC;
    elsif s1_attrhints.attrs == MemAttr_WT or s2_attrhints.attrs == MemAttr_WT:
        attrhints.attrs = MemAttr_WT;
    else:
        attrhints.attrs = MemAttr_WB;
    # Stage 2 does not assign any allocation hints
    # Instead, they are inherited from stage 1
    if attrhints.attrs != MemAttr_NC:
        attrhints.hints     = s1_attrhints.hints;
        attrhints.transient = s1_attrhints.transient;
    return attrhints;
# core.S2CombineS1Device()
# ===================
# Determine resultant Device type1 from combining output memory attributes
# in stage 1 and Device attributes in stage 2
DeviceType core.S2CombineS1Device(DeviceType s1_device, DeviceType s2_device)
    if s1_device == DeviceType_nGnRnE or s2_device == DeviceType_nGnRnE:
        return DeviceType_nGnRnE;
    elsif s1_device == DeviceType_nGnRE or s2_device == DeviceType_nGnRE:
        return DeviceType_nGnRE;
    elsif s1_device == DeviceType_nGRE or s2_device == DeviceType_nGRE:
        return DeviceType_nGRE;
    else:
        return DeviceType_GRE;
# core.S2CombineS1Shareability()
# =========================
# Combine stage 2 shareability with stage 1
Shareability core.S2CombineS1Shareability(Shareability s1_shareability,
                                     Shareability s2_shareability)
    if (s1_shareability == Shareability_OSH or
            s2_shareability == Shareability_OSH) then
        return Shareability_OSH;
    elsif (s1_shareability == Shareability_ISH or
            s2_shareability == Shareability_ISH) then
        return Shareability_ISH;
    else:
        return Shareability_NSH;
# core.HaveMTE2Ext()
# =============
# Returns True if MTE support is beyond EL0, and False otherwise.
boolean core.HaveMTE2Ext()
    return core.IsFeatureImplemented(FEAT_MTE2);
# core.S2MemTagType()
# ==============
# Determine whether the combined output memory attributes of stage 1 and
# stage 2 indicate tagged memory
MemTagType core.S2MemTagType(MemoryAttributes s2_memattrs, MemTagType s1_tagtype)
    if not core.HaveMTE2Ext():
        return MemTag_Untagged;
    if ((s1_tagtype == MemTag_AllocationTagged)  and
        (s2_memattrs.memtype == MemType_Normal)  and
        (s2_memattrs.inner.attrs == MemAttr_WB)  and
        (s2_memattrs.inner.hints == MemHint_RWA) and
        (not s2_memattrs.inner.transient)           and
        (s2_memattrs.outer.attrs == MemAttr_WB)  and
        (s2_memattrs.outer.hints == MemHint_RWA) and
        (not s2_memattrs.outer.transient)) then
        return MemTag_AllocationTagged;
    # Return what stage 1 asked for if we can, otherwise Untagged.
    if s1_tagtype != MemTag_AllocationTagged:
        return s1_tagtype;
    return MemTag_Untagged;
# core.S2CombineS1MemAttrs()
# =====================
# Combine stage 2 with stage 1 memory attributes
MemoryAttributes core.S2CombineS1MemAttrs(MemoryAttributes s1_memattrs, MemoryAttributes s2_memattrs,
                                     boolean s2aarch64)
    MemoryAttributes memattrs;
    if s1_memattrs.memtype == MemType_Device and s2_memattrs.memtype == MemType_Device:
        memattrs.memtype = MemType_Device;
        memattrs.device  = core.S2CombineS1Device(s1_memattrs.device, s2_memattrs.device);
    elsif s1_memattrs.memtype == MemType_Device:
        # S2 Normal, S1 Device
        memattrs = s1_memattrs;
    elsif s2_memattrs.memtype == MemType_Device:
        # S2 Device, S1 Normal
        memattrs = s2_memattrs;
    else                                                # S2 Normal, S1 Normal
        memattrs.memtype = MemType_Normal;
        memattrs.inner   = core.S2CombineS1AttrHints(s1_memattrs.inner, s2_memattrs.inner);
        memattrs.outer   = core.S2CombineS1AttrHints(s1_memattrs.outer, s2_memattrs.outer);
    memattrs.tags = core.S2MemTagType(memattrs, s1_memattrs.tags);
    if not core.HaveMTEPermExt():
        memattrs.notagaccess = False;
    else:
        memattrs.notagaccess = (s2_memattrs.notagaccess and
                               s1_memattrs.tags == MemTag_AllocationTagged);
    memattrs.shareability = core.S2CombineS1Shareability(s1_memattrs.shareability,
                                                    s2_memattrs.shareability);
    if (memattrs.memtype == MemType_Normal and
            memattrs.inner.attrs == MemAttr_WB and
            memattrs.outer.attrs == MemAttr_WB) then
        memattrs.xs = '0';
    elsif s2aarch64:
        memattrs.xs = s2_memattrs.xs & s1_memattrs.xs;
    else:
        memattrs.xs = s1_memattrs.xs;
    memattrs.shareability = core.EffectiveShareability(memattrs);
    return memattrs;
# core.ContiguousSize()
# ================
# Return the number of entries log 2 marking a contiguous output range
integer core.ContiguousSize(bit d128, TGx tgx, integer level)
    if d128 == '1':
        return 4;
    else:
        case tgx of
            when TGx_4KB
                assert level != 0;
                return 4;
            when TGx_16KB
                assert level IN {2, 3};
                return 5 if level == 2 else 7;
            when TGx_64KB
                assert level != 1;
                return 5;
# Permissions
# ===========
# Access Control bits in translation table descriptors
type Permissions is (
    core.bits(2) ap_table,   # Stage 1 hierarchical access permissions
    bit     xn_table,   # Stage 1 hierarchical execute-never for single EL regimes
    bit     pxn_table,  # Stage 1 hierarchical privileged execute-never
    bit     uxn_table,  # Stage 1 hierarchical unprivileged execute-never
    core.bits(3) ap,         # Stage 1 access permissions
    bit     xn,         # Stage 1 execute-never for single EL regimes
    bit     uxn,        # Stage 1 unprivileged execute-never
    bit     pxn,        # Stage 1 privileged execute-never
    core.bits(4) ppi,        # Stage 1 privileged indirect permissions
    core.bits(4) upi,        # Stage 1 unprivileged indirect permissions
    bit     ndirty,     # Stage 1 dirty state for indirect permissions scheme
    core.bits(4) s2pi,       # Stage 2 indirect permissions
    bit     s2dirty,    # Stage 2 dirty state
    core.bits(4) po_index,   # Stage 1 overlay permissions index
    core.bits(4) s2po_index, # Stage 2 overlay permissions index
    core.bits(2) s2ap,       # Stage 2 access permissions
    bit     s2tag_na,   # Stage 2 tag access
    bit     s2xnx,      # Stage 2 extended execute-never
    bit     s2xn        # Stage 2 execute-never
)
# SDFType
# =======
# Short-descriptor format type1
enumeration SDFType {
    SDFType_Table,
    SDFType_Invalid,
    SDFType_Supersection,
    SDFType_Section,
    SDFType_LargePage,
    SDFType_SmallPage
};
# TTWState
# ========
# Translation table walk state
type TTWState is (
    boolean             istable,
    integer             level,
    FullAddress         baseaddress,
    bit                 contiguous,
    boolean             s1assured,      # Stage 1 Assured Translation Property
    bit                 s2assuredonly,  # Stage 2 AssuredOnly attribute
    bit                 disch,          # Stage 1 Disable Contiguous Hint
    bit                 nG,
    bit                 guardedpage,
    SDFType             sdftype,    # AArch32 Short-descriptor format walk only
    core.bits(4)             domain,     # AArch32 Short-descriptor format walk only
    MemoryAttributes    memattrs,
    Permissions         permissions
)
# core.TGxGranuleBits()
# ================
# Retrieve the address size, in bits, of a granule
integer core.TGxGranuleBits(TGx tgx)
    case tgx of
        when TGx_4KB  return 12;
        when TGx_16KB return 14;
        when TGx_64KB return 16;
# core.TranslationSize()
# =================
# Compute the number of bits directly mapped from the input address
# to the output address
integer core.TranslationSize(bit d128, TGx tgx, integer level)
    granulebits = core.TGxGranuleBits(tgx);
    descsizelog2 = 4 if d128 == '1' else 3;
    blockbits   = (FINAL_LEVEL - level) * (granulebits - descsizelog2);
    return granulebits + blockbits;
# core.StageOA()
# =========
# Given the final walk state (a page or block descriptor), map the untranslated
# input address bits to the output address
FullAddress core.StageOA(core.bits(64) ia, bit d128, TGx tgx, TTWState walkstate)
    # Output Address
    FullAddress oa;
    csize = 0;
    tsize = core.TranslationSize(d128, tgx, walkstate.level);
    if walkstate.contiguous == '1':
        csize = core.ContiguousSize(d128, tgx, walkstate.level);
    else:
        csize = 0;
    ia_msb = tsize + csize;
    oa.paspace = walkstate.baseaddress.paspace;
    oa.address = walkstate.baseaddress.address<55:ia_msb>:ia<ia_msb-1:0>;
    return oa;
# AArch64.core.S2Translate()
# =====================
# Translate stage 1 IPA to PA and combine memory attributes
(FaultRecord, AddressDescriptor) AArch64.core.S2Translate(FaultRecord fault_in, AddressDescriptor ipa,
                                                     boolean s1aarch64, boolean aligned,
                                                     AccessDescriptor accdesc)
    walkparams = AArch64.core.GetS2TTWParams(accdesc.ss, ipa.paddress.paspace, s1aarch64);
    FaultRecord fault = fault_in;
    s2fs1mro = False;
    # Prepare fault fields in case a fault is detected
    fault.statuscode  = Fault_None; # Ignore any faults from stage 1
    fault.secondstage = True;
    fault.s2fs1walk   = accdesc.acctype == AccessType_TTW;
    fault.ipaddress   = ipa.paddress;
    if walkparams.vm != '1':
        # Stage 2 translation is disabled
        return (fault, ipa);
    constant integer s2mintxsz = AArch64.core.S2MinTxSZ(walkparams.d128, walkparams.ds,
                                                   walkparams.tgx, s1aarch64);
    constant integer s2maxtxsz = AArch64.core.MaxTxSZ(walkparams.tgx);
    if AArch64.core.S2TxSZFaults(walkparams, s1aarch64):
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    elsif core.UInt(walkparams.txsz) < s2mintxsz:
        walkparams.txsz = core.Field(s2mintxsz,5,0);
    elsif core.UInt(walkparams.txsz) > s2maxtxsz:
        walkparams.txsz = core.Field(s2maxtxsz,5,0);
    if (walkparams.d128 == '0' and
        (AArch64.core.S2InvalidSL(walkparams) or AArch64.core.S2InconsistentSL(walkparams))) then
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    if AArch64.core.IPAIsOutOfRange(ipa.paddress.address, walkparams):
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    AddressDescriptor descpaddr;
    TTWState walkstate;
    descriptor = 0;
    new_desc = 0;
    mem_desc = 0;
    repeat
        if walkparams.d128 == '1':
            (fault, descpaddr, walkstate, descriptor) = AArch64.core.S2Walk(fault, ipa, walkparams,
                                                                       accdesc, 128);
        else:
            (fault, descpaddr, walkstate, core.Field(descriptor,63,0)) = AArch64.core.S2Walk(fault, ipa,
                                                                             walkparams, accdesc,
                                                                             64);
            descriptor = core.SetField(descriptor,127,64,core.Zeros(64));
        if fault.statuscode != Fault_None:
            return (fault, AddressDescriptor UNKNOWN);
        if AArch64.core.S2HasAlignmentFault(accdesc, aligned, walkstate.memattrs):
            fault.statuscode = Fault_Alignment;
        if fault.statuscode == Fault_None:
            (fault, s2fs1mro) = AArch64.core.S2CheckPermissions(fault, walkstate, walkparams, ipa,
                                                           accdesc);
        new_desc = descriptor;
        if walkparams.ha == '1' and AArch64.core.SettingAccessFlagPermitted(fault):
            # Set descriptor AF bit
            new_desc = core.SetBit(new_desc,10,'1')
        # If HW update of dirty bit is enabled, the walk state permissions
        # will already reflect a configuration permitting writes.
        # The update of the descriptor occurs only if the descriptor bits in
        # memory do not reflect that and the access instigates a write.
        if (AArch64.core.SettingDirtyStatePermitted(fault) and
                walkparams.ha  == '1' and
                walkparams.hd  == '1' and
                (walkparams.s2pie == '1' or core.Bit(descriptor,51) == '1') and
                accdesc.write and
                not (accdesc.acctype IN {AccessType_AT, AccessType_IC, AccessType_DC})) then
            # Set descriptor S2AP[1]/Dirty bit permitting stage 2 writes
            new_desc = core.SetBit(new_desc,7,'1')
        # Either the access flag was clear or S2AP[1]/Dirty is clear
        if new_desc != descriptor:
            AccessDescriptor descaccess = core.CreateAccDescTTEUpdate(accdesc);
            if walkparams.d128 == '1':
                (fault, mem_desc) = AArch64.core.MemSwapTableDesc(fault, descriptor, new_desc,
                                                             walkparams.ee, descaccess,
                                                             descpaddr);
            else:
                (fault, core.Field(mem_desc,63,0)) = AArch64.core.MemSwapTableDesc(fault, core.Field(descriptor,63,0),
                                                                   core.Field(new_desc,63,0), walkparams.ee,
                                                                   descaccess, descpaddr);
                mem_desc = core.SetField(mem_desc,127,64,core.Zeros(64));
    until new_desc == descriptor or mem_desc == new_desc;
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN);
    ipa_64 = core.ZeroExtend(ipa.paddress.address, 64);
    # Output Address
    oa = core.StageOA(ipa_64, walkparams.d128, walkparams.tgx, walkstate);
    MemoryAttributes s2_memattrs;
    if ((accdesc.acctype == AccessType_TTW and
            walkstate.memattrs.memtype == MemType_Device and walkparams.ptw == '0') or
        (accdesc.acctype == AccessType_IFETCH and
            (walkstate.memattrs.memtype == MemType_Device or HCR_EL2.ID == '1')) or
        (accdesc.acctype != AccessType_IFETCH and
             walkstate.memattrs.memtype == MemType_Normal and HCR_EL2.CD == '1')) then
        # Treat memory attributes as Normal Non-Cacheable
        s2_memattrs = core.NormalNCMemAttr();
        s2_memattrs.xs = walkstate.memattrs.xs;
    else:
        s2_memattrs = walkstate.memattrs;
    if accdesc.ls64 and s2_memattrs.memtype == MemType_Normal:
        if s2_memattrs.inner.attrs != MemAttr_NC or s2_memattrs.outer.attrs != MemAttr_NC:
            fault.statuscode = Fault_Exclusive;
            return (fault, AddressDescriptor UNKNOWN);
    s2aarch64 = True;
    MemoryAttributes memattrs;
    if walkparams.fwb == '0':
        memattrs = core.S2CombineS1MemAttrs(ipa.memattrs, s2_memattrs, s2aarch64);
    else:
        memattrs = s2_memattrs;
    pa = core.CreateAddressDescriptor(ipa.vaddress, oa, memattrs);
    pa.s2fs1mro = s2fs1mro;
    pa.mecid = AArch64.core.S2OutputMECID(walkparams, pa.paddress.paspace, descriptor);
    return (fault, pa);
# AArch64.core.S1Translate()
# =====================
# Translate VA to IPA/PA depending on the regime
(FaultRecord, AddressDescriptor) AArch64.core.S1Translate(FaultRecord fault_in, Regime regime,
                                                     core.bits(64) va, boolean aligned,
                                                     AccessDescriptor accdesc)
    FaultRecord fault = fault_in;
    # Prepare fault fields in case a fault is detected
    fault.secondstage = False;
    fault.s2fs1walk   = False;
    if not AArch64.core.S1Enabled(regime, accdesc.acctype):
        return AArch64.core.S1DisabledOutput(fault, regime, va, accdesc, aligned);
    walkparams = AArch64.core.GetS1TTWParams(regime, accdesc.ss, va);
    constant integer s1mintxsz = AArch64.core.S1MinTxSZ(regime, walkparams.d128,
                                                   walkparams.ds, walkparams.tgx);
    constant integer s1maxtxsz = AArch64.core.MaxTxSZ(walkparams.tgx);
    if AArch64.core.S1TxSZFaults(regime, walkparams):
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    elsif core.UInt(walkparams.txsz) < s1mintxsz:
        walkparams.txsz = core.Field(s1mintxsz,5,0);
    elsif core.UInt(walkparams.txsz) > s1maxtxsz:
        walkparams.txsz = core.Field(s1maxtxsz,5,0);
    if AArch64.core.VAIsOutOfRange(va, accdesc.acctype, regime, walkparams):
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    if accdesc.el == EL0 and walkparams.e0pd == '1':
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    if core.HaveTME() and accdesc.el == EL0 and walkparams.nfd == '1' and accdesc.transactional:
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    if core.HaveSVE() and accdesc.el == EL0 and walkparams.nfd == '1' and (
            (accdesc.nonfault and accdesc.contiguous) or
            (accdesc.firstfault and not accdesc.first and not accdesc.contiguous)) then
        fault.statuscode = Fault_Translation;
        fault.level      = 0;
        return (fault, AddressDescriptor UNKNOWN);
    AddressDescriptor descipaddr;
    TTWState walkstate;
    descriptor = 0;
    new_desc = 0;
    mem_desc = 0;
    repeat
        if walkparams.d128 == '1':
            (fault, descipaddr, walkstate, descriptor) = AArch64.core.S1Walk(fault, walkparams, va,
                                                                        regime, accdesc, 128);
        else:
            (fault, descipaddr, walkstate, core.Field(descriptor,63,0)) = AArch64.core.S1Walk(fault, walkparams,
                                                                              va, regime, accdesc,
                                                                              64);
            descriptor = core.SetField(descriptor,127,64,core.Zeros(64));
        if fault.statuscode != Fault_None:
            return (fault, AddressDescriptor UNKNOWN);
        if accdesc.acctype == AccessType_IFETCH:
            # Flag the fetched instruction is from a guarded page
            core.SetInGuardedPage(walkstate.guardedpage == '1');
        if AArch64.core.S1HasAlignmentFault(accdesc, aligned, walkparams.ntlsmd,
                                       walkstate.memattrs) then
            fault.statuscode = Fault_Alignment;
        if fault.statuscode == Fault_None:
            fault = AArch64.core.S1CheckPermissions(fault, regime, walkstate, walkparams, accdesc);
        new_desc = descriptor;
        if walkparams.ha == '1' and AArch64.core.SettingAccessFlagPermitted(fault):
            # Set descriptor AF bit
            new_desc = core.SetBit(new_desc,10,'1')
        # If HW update of dirty bit is enabled, the walk state permissions
        # will already reflect a configuration permitting writes.
        # The update of the descriptor occurs only if the descriptor bits in
        # memory do not reflect that and the access instigates a write.
        if (AArch64.core.SettingDirtyStatePermitted(fault) and
                walkparams.ha  == '1' and
                walkparams.hd  == '1' and
                (walkparams.pie == '1' or core.Bit(descriptor,51) == '1') and
                accdesc.write and
                not (accdesc.acctype IN {AccessType_AT, AccessType_IC, AccessType_DC})) then
            # Clear descriptor AP[2]/nDirty bit permitting stage 1 writes
            new_desc = core.SetBit(new_desc,7,'0')
        # Either the access flag was clear or AP[2]/nDirty is set
        if new_desc != descriptor:
            AddressDescriptor descpaddr;
            descaccess = core.CreateAccDescTTEUpdate(accdesc);
            if regime == Regime_EL10 and core.EL2Enabled():
                FaultRecord s2fault;
                s1aarch64 = True;
                s2aligned = True;
                (s2fault, descpaddr) = AArch64.core.S2Translate(fault, descipaddr, s1aarch64, s2aligned,
                                                           descaccess);
                if s2fault.statuscode != Fault_None:
                    return (s2fault, AddressDescriptor UNKNOWN);
            else:
                descpaddr = descipaddr;
            if walkparams.d128 == '1':
                (fault, mem_desc) = AArch64.core.MemSwapTableDesc(fault, descriptor, new_desc,
                                                             walkparams.ee, descaccess, descpaddr);
            else:
                (fault, core.Field(mem_desc,63,0)) = AArch64.core.MemSwapTableDesc(fault, core.Field(descriptor,63,0),
                                                                   core.Field(new_desc,63,0), walkparams.ee,
                                                                   descaccess, descpaddr);
                mem_desc = core.SetField(mem_desc,127,64,core.Zeros(64));
    until new_desc == descriptor or mem_desc == new_desc;
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN);
    # Output Address
    oa = core.StageOA(va, walkparams.d128, walkparams.tgx, walkstate);
    MemoryAttributes memattrs;
    if (accdesc.acctype == AccessType_IFETCH and
        (walkstate.memattrs.memtype == MemType_Device or not AArch64.core.S1ICacheEnabled(regime))) then
        # Treat memory attributes as Normal Non-Cacheable
        memattrs = core.NormalNCMemAttr();
        memattrs.xs = walkstate.memattrs.xs;
    elsif (accdesc.acctype != AccessType_IFETCH and not AArch64.core.S1DCacheEnabled(regime) and
             walkstate.memattrs.memtype == MemType_Normal) then
        # Treat memory attributes as Normal Non-Cacheable
        memattrs = core.NormalNCMemAttr();
        memattrs.xs = walkstate.memattrs.xs;
        # The effect of SCTLR_ELx.C when '0' is Constrained raise Exception('UNPREDICTABLE')
        # on the Tagged attribute
        if (core.HaveMTE2Ext() and walkstate.memattrs.tags == MemTag_AllocationTagged and
            not core.ConstrainUnpredictableBool(Unpredictable_S1CTAGGED)) then
            memattrs.tags = MemTag_Untagged;
    else:
        memattrs = walkstate.memattrs;
    # Shareability value of stage 1 translation subject to stage 2 is IMPLEMENTATION DEFINED
    # to be either effective value or descriptor value
    if (regime == Regime_EL10 and core.EL2Enabled() and HCR_EL2.VM == '1' and
            not (boolean IMPLEMENTATION_DEFINED "Apply effective shareability at stage 1")) then
        memattrs.shareability = walkstate.memattrs.shareability;
    else:
        memattrs.shareability = core.EffectiveShareability(memattrs);
    if accdesc.ls64 and memattrs.memtype == MemType_Normal:
        if memattrs.inner.attrs != MemAttr_NC or memattrs.outer.attrs != MemAttr_NC:
            fault.statuscode = Fault_Exclusive;
            return (fault, AddressDescriptor UNKNOWN);
    ipa = core.CreateAddressDescriptor(va, oa, memattrs);
    ipa.s1assured = walkstate.s1assured;
    varange   = AArch64.core.GetVARange(va);
    ipa.mecid = AArch64.core.S1OutputMECID(walkparams, regime, varange, ipa.paddress.paspace,
                                      descriptor);
    return (fault, ipa);
# core.CreateFaultyAddressDescriptor()
# ===============================
# Set internal members for address descriptor type1 with values indicating error
AddressDescriptor core.CreateFaultyAddressDescriptor(core.bits(64) va, FaultRecord fault)
    AddressDescriptor addrdesc;
    addrdesc.vaddress = va;
    addrdesc.fault    = fault;
    return addrdesc;
# core.TranslationRegime()
# ===================
# Select the translation regime given the target EL and PE state
Regime core.TranslationRegime(core.bits(2) el)
    if el == EL3:
        return Regime_EL30 if core.ELUsingAArch32(EL3) else Regime_EL3;
    elsif el == EL2:
        return Regime_EL20 if core.ELIsInHost(EL2) else Regime_EL2;
    elsif el == EL1:
        return Regime_EL10;
    elsif el == EL0:
        if core.CurrentSecurityState() == SS_Secure and core.ELUsingAArch32(EL3):
            return Regime_EL30;
        elsif core.ELIsInHost(EL0):
            return Regime_EL20;
        else:
            return Regime_EL10;
    else:
        core.Unreachable();
# AArch64.core.FullTranslate()
# =======================
# Address translation as specified by VMSA
# Alignment check NOT due to memory type1 is expected to be done before translation
AddressDescriptor AArch64.core.FullTranslate(core.bits(64) va, AccessDescriptor accdesc, boolean aligned)
    Regime regime = core.TranslationRegime(accdesc.el);
    FaultRecord fault = core.NoFault(accdesc);
    AddressDescriptor ipa;
    (fault, ipa) = AArch64.core.S1Translate(fault, regime, va, aligned, accdesc);
    if fault.statuscode != Fault_None:
        return core.CreateFaultyAddressDescriptor(va, fault);
    assert (accdesc.ss == SS_Realm) IMPLIES core.EL2Enabled();
    if regime == Regime_EL10 and core.EL2Enabled():
        s1aarch64 = True;
        AddressDescriptor pa;
        (fault, pa) = AArch64.core.S2Translate(fault, ipa, s1aarch64, aligned, accdesc);
        if fault.statuscode != Fault_None:
            return core.CreateFaultyAddressDescriptor(va, fault);
        else:
            return pa;
    else:
        return ipa;
# core.SPEStartCounter()
# =================
# Enables incrementing of the counter at the passed index when SPECycle is called.
core.SPEStartCounter(integer counter_index)
    assert counter_index < SPEMaxCounters;
    SPESampleCounterPending[counter_index] = True;
# core.SPEStopCounter()
# ================
# Disables incrementing of the counter at the passed index when SPECycle is called.
core.SPEStopCounter(integer counter_index)
    SPESampleCounterValid[counter_index] = True;
    SPESampleCounterPending[counter_index] = False;
# AArch64.core.TranslateAddress()
# ==========================
# Main entry point for translating an address
AddressDescriptor AArch64.core.TranslateAddress(core.bits(64) va, AccessDescriptor accdesc,
                                           boolean aligned, integer size)
    if (SPESampleInFlight and not (accdesc.acctype IN {AccessType_IFETCH,
                                                   AccessType_SPE})) then
        core.SPEStartCounter(SPECounterPosTranslationLatency);
    AddressDescriptor result = AArch64.core.FullTranslate(va, accdesc, aligned);
    if not core.IsFault(result) and accdesc.acctype != AccessType_IFETCH:
        result.fault = AArch64.core.CheckDebug(va, accdesc, size);
    if core.HaveRME() and not core.IsFault(result) and (
            accdesc.acctype != AccessType_DC or
            boolean IMPLEMENTATION_DEFINED "GPC Fault on DC operations") then
        result.fault.gpcf = core.GranuleProtectionCheck(result, accdesc);
        if result.fault.gpcf.gpf != GPCF_None:
            result.fault.statuscode = Fault_GPCFOnOutput;
            result.fault.paddress   = result.paddress;
    if not core.IsFault(result) and accdesc.acctype == AccessType_IFETCH:
        result.fault = AArch64.core.CheckDebug(va, accdesc, size);
    if (SPESampleInFlight and not (accdesc.acctype IN {AccessType_IFETCH,
                                                   AccessType_SPE})) then
        core.SPEStopCounter(SPECounterPosTranslationLatency);
    # Update virtual address for abort functions
    result.vaddress = core.ZeroExtend(va, 64);
    return result;
# core.DebugMemWrite()
# ===============
# Write data to memory one byte at a time. Starting at the passed virtual address.
# Used by SPE.
(PhysMemRetStatus, AddressDescriptor) core.DebugMemWrite(core.bits(64) vaddress, AccessDescriptor accdesc,
                                                    boolean aligned, core.bits(8) data)
    PhysMemRetStatus memstatus = PhysMemRetStatus UNKNOWN;
    # Translate virtual address
    AddressDescriptor addrdesc;
    integer size = 1;
    addrdesc = AArch64.core.TranslateAddress(vaddress, accdesc, aligned, size);
    if core.IsFault(addrdesc):
        return (memstatus, addrdesc);
    memstatus = core.PhysMemWrite(addrdesc, 1, accdesc, data);
    return (memstatus, addrdesc);
# core.Have52BitIPAAndPASpaceExt()
# ===========================
# Returns True if 52-bit IPA and PA extension support
# is implemented, and False otherwise.
boolean core.Have52BitIPAAndPASpaceExt()
    return core.IsFeatureImplemented(FEAT_LPA2);
# core.Have56BitPAExt()
# ================
# Returns True if 56-bit Physical Address extension
# support is implemented and False otherwise.
boolean core.Have56BitPAExt()
    return core.IsFeatureImplemented(FEAT_D128);
# core.EncodeLDFSC()
# =============
# Function that gives the Long-descriptor FSC code for types of Fault
core.bits(6) core.EncodeLDFSC(Fault statuscode, integer level)
    result = 0;
    # 128-bit descriptors will start from level -2 for 4KB to resolve bits IA[55:51]
    if level == -2:
        assert core.Have56BitPAExt();
        case statuscode of
            when Fault_AddressSize          result = '101100';
            when Fault_Translation          result = '101010';
            when Fault_SyncExternalOnWalk   result = '010010';
            when Fault_SyncParityOnWalk     result = '011010'; assert not core.HaveRASExt();
            when Fault_GPCFOnWalk           result = '100010';
            otherwise                       core.Unreachable();
        return result;
    if level == -1:
        assert core.Have52BitIPAAndPASpaceExt();
        case statuscode of
            when Fault_AddressSize          result = '101001';
            when Fault_Translation          result = '101011';
            when Fault_SyncExternalOnWalk   result = '010011';
            when Fault_SyncParityOnWalk     result = '011011'; assert not core.HaveRASExt();
            when Fault_GPCFOnWalk           result = '100011';
            otherwise                       core.Unreachable();
        return result;
    case statuscode of
        when Fault_AddressSize         result = '0000':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_AccessFlag          result = '0010':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_Permission          result = '0011':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_Translation         result = '0001':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_SyncExternal        result = '010000';
        when Fault_SyncExternalOnWalk  result = '0101':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_SyncParity          result = '011000';
        when Fault_SyncParityOnWalk    result = '0111':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_AsyncParity         result = '011001';
        when Fault_AsyncExternal       result = '010001'; assert core.UsingAArch32();
        when Fault_TagCheck            result = '010001'; assert core.HaveMTE2Ext();
        when Fault_Alignment           result = '100001';
        when Fault_Debug               result = '100010';
        when Fault_GPCFOnWalk          result = '1001':core.Field(level,1,0); assert level IN {0,1,2,3};
        when Fault_GPCFOnOutput        result = '101000';
        when Fault_TLBConflict         result = '110000';
        when Fault_HWUpdateAccessFlag  result = '110001';
        when Fault_Lockdown            result = '110100';  # IMPLEMENTATION DEFINED
        when Fault_Exclusive           result = '110101';  # IMPLEMENTATION DEFINED
        otherwise                      core.Unreachable();
    return result;
# core.DebugWriteExternalAbort()
# =========================
# Populate the syndrome register for an External abort caused by a call of core.DebugMemWrite().
core.DebugWriteExternalAbort(PhysMemRetStatus memstatus, AddressDescriptor addrdesc,
                        core.bits(64) start_vaddr)
    boolean iswrite = True;
    boolean handle_as_SError = False;
    boolean async_external_abort = False;
    syndrome = 0;
    case addrdesc.fault.access.acctype of
        when AccessType_SPE
            handle_as_SError = boolean IMPLEMENTATION_DEFINED "SPE SyncExternal as SError";
            async_external_abort = boolean IMPLEMENTATION_DEFINED "SPE async External abort";
            syndrome = core.Field(PMBSR_EL1,63,0);
        otherwise
            core.Unreachable();
    ttw_abort = False;
    ttw_abort = addrdesc.fault.statuscode IN {Fault_SyncExternalOnWalk,
                                              Fault_SyncParityOnWalk};
    Fault statuscode = addrdesc.fault.statuscode if ttw_abort else memstatus.statuscode;
    bit extflag = addrdesc.fault.extflag if ttw_abort else memstatus.extflag;
    if (statuscode IN {Fault_AsyncExternal, Fault_AsyncParity} or handle_as_SError):
        # ASYNC Fault -> SError or SYNC Fault handled as SError
        FaultRecord fault = core.NoFault();
        boolean parity = statuscode IN {Fault_SyncParity, Fault_AsyncParity,
                                        Fault_SyncParityOnWalk};
        fault.statuscode = Fault_AsyncParity if parity else Fault_AsyncExternal;
        if core.HaveRASExt():
            fault.merrorstate = memstatus.merrorstate;
        fault.extflag = extflag;
        fault.access.acctype = addrdesc.fault.access.acctype;
        core.PendSErrorInterrupt(fault);
    else:
        # SYNC Fault, not handled by SError
        # Generate Buffer Management Event
        # EA bit
        syndrome = core.SetBit(syndrome,18,'1')
        # DL bit for SPE
        if addrdesc.fault.access.acctype == AccessType_SPE and (async_external_abort or
            (start_vaddr != addrdesc.vaddress)) then
            syndrome = core.SetBit(syndrome,19,'1')
        # Do not change following values if previous Buffer Management Event
        # has not been handled.
        # S bit
        if core.IsZero(core.Bit(syndrome,17)):
            syndrome = core.SetBit(syndrome,17,'1')
            # EC bits
            ec = 0;
            if (core.HaveRME() and addrdesc.fault.gpcf.gpf != GPCF_None and
                addrdesc.fault.gpcf.gpf != GPCF_Fail) then
                ec = '011110';
            else:
                ec = '100101' if addrdesc.fault.secondstage else '100100';
            syndrome = core.SetField(syndrome,31,26,ec);
            # MSS bits
            if async_external_abort:
                syndrome = core.SetField(syndrome,15,0,core.Zeros(10) : '010001');
            else:
                syndrome = core.SetField(syndrome,15,0,core.Zeros(10) : core.EncodeLDFSC(statuscode, addrdesc.fault.level));
        case addrdesc.fault.access.acctype of
            when AccessType_SPE
                PMBSR_EL1 = core.SetField(PMBSR_EL1,63,0,syndrome);
            otherwise
                core.Unreachable();
# core.DebugWriteFault()
# =================
# Populate the syndrome register for a Translation fault caused by a call of core.DebugMemWrite().
core.DebugWriteFault(core.bits(64) vaddress, FaultRecord fault)
    syndrome = 0;
    case fault.access.acctype of
        when AccessType_SPE
            syndrome = core.Field(PMBSR_EL1,63,0);
        otherwise
            core.Unreachable();
    # MSS
    syndrome = core.SetField(syndrome,15,0,core.Zeros(10) : core.EncodeLDFSC(fault.statuscode, fault.level));
    # MSS2
    syndrome = core.SetField(syndrome,55,32,core.Zeros(24));
    # EC bits
    ec = 0;
    if core.HaveRME() and fault.gpcf.gpf != GPCF_None and fault.gpcf.gpf != GPCF_Fail:
        ec = '011110';
    else:
        ec = '100101' if fault.secondstage else '100100';
    syndrome = core.SetField(syndrome,31,26,ec);
    # S bit
    syndrome = core.SetBit(syndrome,17,'1')
    if fault.statuscode == Fault_Permission:
        # assuredonly bit
        syndrome = core.SetBit(syndrome,39,'1' if fault.assuredonly else '0')
        # overlay bit
        syndrome = core.SetBit(syndrome,38,'1' if fault.overlay else '0')
        # dirtybit
        syndrome = core.SetBit(syndrome,37,'1' if fault.dirtybit else '0')
    case fault.access.acctype of
        when AccessType_SPE
            PMBSR_EL1 = core.SetField(PMBSR_EL1,63,0,syndrome);
        otherwise
            core.Unreachable();
    # Buffer Write Pointer already points to the address that generated the fault.
    # Writing to memory never started so no data loss. DL is unchanged.
    return;
# core.SPEWriteToBuffer()
# ==================
# Write the active record to the Profiling Buffer.
core.SPEWriteToBuffer()
    assert core.ProfilingBufferEnabled();
    # Check alignment
    boolean aligned = core.IsZero(PMBPTR_EL1.PTR<core.UInt(PMBIDR_EL1.Align)-1:0>);
    ttw_fault_as_external_abort = False;
    ttw_fault_as_external_abort = boolean IMPLEMENTATION_DEFINED "SPE TTW fault External abort";
    FaultRecord fault;
    PhysMemRetStatus memstatus;
    AddressDescriptor addrdesc;
    AccessDescriptor accdesc;
    SecurityState owning_ss;
    owning_el = 0;
    (owning_ss, owning_el) = core.ProfilingBufferOwner();
    accdesc = core.CreateAccDescSPE(owning_ss, owning_el);
    core.bits(64) start_vaddr = core.Field(PMBPTR_EL1,63,0);
    for i = 0 to SPERecordSize - 1
        # If a previous write did not cause an issue
        if PMBSR_EL1.S == '0':
            (memstatus, addrdesc) = core.DebugMemWrite(core.Field(PMBPTR_EL1,63,0), accdesc, aligned,
                                                  SPERecordData[i]);
            fault = addrdesc.fault;
            ttw_fault = False;
            ttw_fault = fault.statuscode IN {Fault_SyncExternalOnWalk, Fault_SyncParityOnWalk};
            if core.IsFault(fault.statuscode) and not (ttw_fault and ttw_fault_as_external_abort):
                core.DebugWriteFault(core.Field(PMBPTR_EL1,63,0), fault);
            elsif core.IsFault(memstatus) or (ttw_fault and ttw_fault_as_external_abort):
                core.DebugWriteExternalAbort(memstatus, addrdesc, start_vaddr);
            # Move pointer if no Buffer Management Event has been caused.
            if core.IsZero(PMBSR_EL1.S):
                PMBPTR_EL1 = PMBPTR_EL1 + 1;
    return;
# core.SPEConstructRecord()
# ====================
# Create new record and populate it with packets using sample storage data.
# This is an example implementation, packets may appear in
# any order as long as the record ends with an End or Timestamp packet.
core.SPEConstructRecord()
    payload_size = 0;
    # Empty the record.
    core.SPEEmptyRecord();
    # Add contextEL1 if available
    if SPESampleContextEL1Valid:
        core.SPEAddPacketToRecord('01', '0100', SPESampleContextEL1);
     # Add contextEL2 if available
    if SPESampleContextEL2Valid:
        core.SPEAddPacketToRecord('01', '0101', SPESampleContextEL2);
    # Add valid counters
    for counter_index = 0 to (SPEMaxCounters - 1)
        if SPESampleCounterValid[counter_index]:
            if counter_index >= 8:
                # Need extended format
                core.SPEAddByteToRecord('001000':core.Field(counter_index,4,3));
            # Check for overflow
            boolean large_counters = boolean IMPLEMENTATION_DEFINED "SPE 16bit counters";
            if SPESampleCounter[counter_index] > 0xFFFF and large_counters:
                SPESampleCounter[counter_index] = 0xFFFF;
            elsif SPESampleCounter[counter_index] > 0xFFF:
                SPESampleCounter[counter_index] = 0xFFF;
            # Add byte0 for short format (byte1 for extended format)
            core.SPEAddPacketToRecord('10', '1':core.Field(counter_index,2,0),
                core.Field(SPESampleCounter[counter_index],15,0));
    # Add valid addresses
    if core.HaveStatisticalProfilingv1p2():
        # Under the some conditions, it is IMPLEMENTATION_DEFINED whether
        # previous branch packet is present.
        boolean include_prev_br = boolean IMPLEMENTATION_DEFINED "SPE get prev br if not br";
        if SPESampleOpType != OpType_Branch and not include_prev_br:
            SPESampleAddressValid[SPEAddrPosPrevBranchTarget] = False;
    # Data Virtual address should not be collected if this was an NV2 access and Statistical
    # Profiling is disabled at EL2.
    if not core.StatisticalProfilingEnabled(EL2) and SPESampleInstIsNV2:
        SPESampleAddressValid[SPEAddrPosDataVirtual] = False;
    for address_index = 0 to (SPEMaxAddrs - 1)
        if SPESampleAddressValid[address_index]:
            if address_index >= 8:
                # Need extended format
                core.SPEAddByteToRecord('001000':core.Field(address_index,4,3));
            # Add byte0 for short format (byte1 for extended format)
            core.SPEAddPacketToRecord('10', '0':core.Field(address_index,2,0),
                SPESampleAddress[address_index]);
    # Add Data Source
    if SPESampleDataSourceValid:
        payload_size = core.SPEGetDataSourcePayloadSize();
        core.SPEAddPacketToRecord('01', '0011', SPESampleDataSource<8*payload_size-1:0>);
    # Add operation details
    core.SPEAddPacketToRecord('01', '10':SPESampleClass, SPESampleSubclass);
    # Add events
    # Get size of payload in bytes.
    payload_size = core.SPEGetEventsPayloadSize();
    core.SPEAddPacketToRecord('01', '0010', SPESampleEvents<8*payload_size-1:0>);
    # Add Timestamp to end the record if one is available.
    # Otherwise end with an End packet.
    if SPESampleTimestampValid:
        core.SPEAddPacketToRecord('01', '0001', SPESampleTimestamp);
    else:
        core.SPEAddByteToRecord('00000001');
    # Add padding
    while SPERecordSize MOD (1<<core.UInt(PMBIDR_EL1.Align)) != 0 do
        core.SPEAddByteToRecord(core.Zeros(8));
    core.SPEWriteToBuffer();
constant integer SPEAddrPosPCVirtual = 0;
constant integer SPEAddrPosBranchTarget = 1;
constant integer SPEAddrPosDataVirtual = 2;
constant integer SPEAddrPosDataPhysical = 3;
constant integer SPEAddrPosPrevBranchTarget = 4;
constant integer SPECounterPosTotalLatency = 0;
constant integer SPECounterPosIssueLatency = 1;
constant integer SPECounterPosTranslationLatency = 2;
boolean SPESampleInFlight = False;
SPESampleContextEL1 = 0;
SPESampleContextEL1Valid = False;
SPESampleContextEL2 = 0;
SPESampleContextEL2Valid = False;
boolean SPESampleInstIsNV2 = False;
SPESamplePreviousBranchAddress = 0;
SPESamplePreviousBranchAddressValid = False;
SPESampleDataSource = 0;
SPESampleDataSourceValid = False;
OpType SPESampleOpType;
SPESampleClass = 0;
SPESampleSubclass = 0;
SPESampleSubclassValid = False;
SPESampleTimestamp = 0;
SPESampleTimestampValid = False;
SPESampleEvents = 0;
# core.SPEPostExecution()
# ==================
# Called after every executed instruction.
core.SPEPostExecution()
    if SPESampleInFlight:
        SPESampleInFlight = False;
        core.PMUEvent(PMU_EVENT_SAMPLE_FEED);
        # Stop any pending counters
        for counter_index = 0 to (SPEMaxCounters - 1)
            if SPESampleCounterPending[counter_index]:
                core.SPEStopCounter(counter_index);
        boolean discard = False;
        if core.HaveStatisticalProfilingv1p2():
            discard = PMBLIMITR_EL1.FM == '10';
        if core.SPECollectRecord(SPESampleEvents,
                            SPESampleCounter[SPECounterPosTotalLatency],
                            SPESampleOpType) and not discard then
            core.SPEConstructRecord();
            if core.SPEBufferIsFull():
                core.SPEBufferFilled();
        core.SPEResetSampleStorage();
# Counter storage
array [0..SPEMaxCounters-1] of SPESampleCounter = 0;
array [0..SPEMaxCounters-1] of SPESampleCounterValid = False;
array [0..SPEMaxCounters-1] of SPESampleCounterPending = False;
# Address storage
array [0..SPEMaxAddrs-1] of SPESampleAddress = 0;
array [0..SPEMaxAddrs-1] of SPESampleAddressValid = False;
# core.SPEEvent()
# ==========
# Called by PMUEvent if a sample is in flight.
# Sets appropriate bit in SPESampleStorage.events.
core.SPEEvent(core.bits(16) event)
    case event of
        when PMU_EVENT_DSNP_HIT_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,23,'1')
        when PMU_EVENT_L1D_LFB_HIT_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,22,'1')
        when PMU_EVENT_L2D_LFB_HIT_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,22,'1')
        when PMU_EVENT_L3D_LFB_HIT_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,22,'1')
        when PMU_EVENT_LL_LFB_HIT_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,22,'1')
        when PMU_EVENT_L1D_CACHE_HITM_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,21,'1')
        when PMU_EVENT_L2D_CACHE_HITM_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,21,'1')
        when PMU_EVENT_L3D_CACHE_HITM_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,21,'1')
        when PMU_EVENT_LL_CACHE_HITM_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,21,'1')
        when PMU_EVENT_L2D_CACHE_LMISS_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,20,'1')
        when PMU_EVENT_L2D_CACHE_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,19,'1')
        when PMU_EVENT_SVE_PRED_EMPTY_SPEC
            if core.HaveStatisticalProfilingv1p1():
                SPESampleEvents = core.SetBit(SPESampleEvents,18,'1')
        when PMU_EVENT_SVE_PRED_PARTIAL_SPEC
            if core.HaveStatisticalProfilingv1p1():
                SPESampleEvents = core.SetBit(SPESampleEvents,17,'1')
        when PMU_EVENT_LDST_ALIGN_LAT
            if core.HaveStatisticalProfilingv1p1():
                SPESampleEvents = core.SetBit(SPESampleEvents,11,'1')
        when PMU_EVENT_REMOTE_ACCESS         SPESampleEvents = core.SetBit(SPESampleEvents,10,'1')
        when PMU_EVENT_LL_CACHE_MISS         SPESampleEvents = core.SetBit(SPESampleEvents,9,'1')
        when PMU_EVENT_LL_CACHE              SPESampleEvents = core.SetBit(SPESampleEvents,8,'1')
        when PMU_EVENT_BR_MIS_PRED           SPESampleEvents = core.SetBit(SPESampleEvents,7,'1')
        when PMU_EVENT_BR_MIS_PRED_RETIRED   SPESampleEvents = core.SetBit(SPESampleEvents,7,'1')
        when PMU_EVENT_DTLB_WALK             SPESampleEvents = core.SetBit(SPESampleEvents,5,'1')
        when PMU_EVENT_L1D_TLB               SPESampleEvents = core.SetBit(SPESampleEvents,4,'1')
        when PMU_EVENT_L1D_CACHE_REFILL
            if not core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,3,'1')
        when PMU_EVENT_L1D_CACHE_LMISS_RD
            if core.HaveStatisticalProfilingv1p4():
                SPESampleEvents = core.SetBit(SPESampleEvents,3,'1')
        when PMU_EVENT_L1D_CACHE             SPESampleEvents = core.SetBit(SPESampleEvents,2,'1')
        when PMU_EVENT_INST_RETIRED          SPESampleEvents = core.SetBit(SPESampleEvents,1,'1')
        when PMU_EVENT_EXC_TAKEN             SPESampleEvents = core.SetBit(SPESampleEvents,0,'1')
        otherwise return;
    return;
# core.PMUEvent()
# ==========
# Generate a PMU event. By default, increment by 1.
core.PMUEvent(core.bits(16) event)
    core.PMUEvent(event, 1);
# core.PMUEvent()
# ==========
# Accumulate a PMU Event.
core.PMUEvent(core.bits(16) event, integer increment)
    if SPESampleInFlight:
        core.SPEEvent(event);
    integer counters = core.GetNumEventCounters();
    if counters != 0:
        for idx = 0 to counters - 1
            core.PMUEvent(event, increment, idx);
    if core.HaveAArch64() and core.HavePMUv3ICNTR() and event == PMU_EVENT_INST_RETIRED:
        core.IncrementInstructionCounter(increment);
# core.PMUEvent()
# ==========
# Accumulate a PMU Event for a specific event counter.
core.PMUEvent(core.bits(16) event, integer increment, integer idx)
    if not core.HavePMUv3():
        return;
    if core.UsingAArch32():
        if PMEVTYPEcore.R[idx].evtCount == event:
            PMUEventAccumulator[idx] = PMUEventAccumulator[idx] + increment;
    else:
        if PMEVTYPER_EL0[idx].evtCount == event:
            PMUEventAccumulator[idx] = PMUEventAccumulator[idx] + increment;
# core.GetBRBENumRecords()
# ===================
# Returns the number of branch records implemented.
integer core.GetBRBENumRecords()
    assert core.UInt(BRBIDR0_EL1.NUMREC) IN {0x08, 0x10, 0x20, 0x40};
    return integer IMPLEMENTATION_DEFINED "Number of BRB records";
# core.UpdateBranchRecordBuffer()
# ==========================
# Add a new Branch record to the buffer.
core.UpdateBranchRecordBuffer(bit ccu, core.bits(14) cc, bit lastfailed, bit transactional,
                         core.bits(6) branch_type, core.bits(2) el, bit mispredict, core.bits(2) valid,
                         core.bits(64) source_address, core.bits(64) target_address)
    # Shift the Branch Records in the buffer
    for i = core.GetBRBENumRecords() - 1 downto 1
        Records_SRC[i] = Records_SRC[i - 1];
        Records_TGT[i] = Records_TGT[i - 1];
        Records_INF[i] = Records_INF[i - 1];
    Records_INF[0].CCU        = ccu;
    Records_INF[0].CC         = cc;
    Records_INF[0].EL         = el;
    Records_INF[0].VALID      = valid;
    Records_INF[0].T          = transactional;
    Records_INF[0].LASTFAILED = lastfailed;
    Records_INF[0].MPRED      = mispredict;
    Records_INF[0].TYPE       = branch_type;
    Records_SRC[0] = source_address;
    Records_TGT[0] = target_address;
    return;
# core.BRBEBranch()
# ============
# Called to write branch record for the following branches when BRB is active:
# direct branches,
# indirect branches,
# direct branches with link,
# indirect branches with link,
# returns from subroutines.
core.BRBEBranch(BranchType br_type, boolean cond, core.bits(64) target_address)
    if core.BranchRecordAllowed(core.APSR.EL) and core.FilterBranchRecord(br_type, cond):
        branch_type = 0;
        case br_type of
            when 'DIR'
                branch_type = '001000' if cond else '000000';
            when 'INDIR'      branch_type = '000001';
            when 'DIRCALL'    branch_type = '000010';
            when 'INDCALL'    branch_type = '000011';
            when 'RET'        branch_type = '000101';
            otherwise                  core.Unreachable();
        bit ccu;
        cc = 0;
        (ccu, cc) = core.BranchEncCycleCount();
        bit lastfailed = BRBFCR_EL1.LASTFAILED if core.HaveTME() else '0';
        bit transactional = '1' if core.HaveTME() and TSTATE.depth > 0 else '0';
        core.bits(2) el = core.APSR.EL;
        bit mispredict = '1' if core.BRBEMispredictAllowed() and core.BranchMispredict() else '0';
        core.UpdateBranchRecordBuffer(ccu, cc, lastfailed, transactional, branch_type, el, mispredict,
                                 '11', PC[], target_address);
        BRBFCR_EL1.LASTFAILED = '0';
        core.PMUEvent(PMU_EVENT_BRB_FILTRATE);
    return;
# core.Hint_Branch()
# =============
# Report the hint passed to core.BranchTo() and core.BranchToAddr(), for consideration when processing
# the next instruction.
core.Hint_Branch(BranchType hint);
# core.SPEBranch()
# ===========
# Called on every branch if SPE is present. Maintains previous branch target
# and branch related SPE functionality.
core.SPEBranch(core.bits(N) target, BranchType branch_type, boolean conditional, boolean taken_flag)
    boolean is_isb = False;
    core.SPEBranch(target, branch_type, conditional, taken_flag, is_isb);
core.SPEBranch(core.bits(N) target, BranchType branch_type, boolean conditional, boolean taken_flag,
          boolean is_isb)
    # If the PE implements branch prediction, data about (mis)prediction is collected
    # through the PMU events.
    collect_prev_br = False;
    boolean collect_prev_br_eret = boolean IMPLEMENTATION_DEFINED "SPE prev br on eret";
    boolean collect_prev_br_exception = boolean IMPLEMENTATION_DEFINED "SPE prev br on exception";
    boolean collect_prev_br_isb = boolean IMPLEMENTATION_DEFINED "SPE prev br on isb";
    case branch_type of
        when 'EXCEPTION'
            collect_prev_br = collect_prev_br_exception;
        when 'ERET'
            collect_prev_br = collect_prev_br_eret;
        otherwise
            collect_prev_br = not is_isb or collect_prev_br_isb;
    # Implements previous branch target functionality
    if (taken_flag and not core.IsZero(PMSIDR_EL1.PBT) and core.StatisticalProfilingEnabled() and
            collect_prev_br) then
        if SPESampleInFlight:
            # Save the target address for it to be added to record.
            core.bits(64) previous_target = SPESamplePreviousBranchAddress;
            SPESampleAddress[SPEAddrPosPrevBranchTarget] = core.SetField(SPESampleAddress[SPEAddrPosPrevBranchTarget],63,0,core.Field(previous_target,63,0));
            boolean previous_branch_valid = SPESamplePreviousBranchAddressValid;
            SPESampleAddressValid[SPEAddrPosPrevBranchTarget] = previous_branch_valid;
        SPESamplePreviousBranchAddress = core.SetField(SPESamplePreviousBranchAddress,55,0,core.Field(target,55,0));
        bit ns;
        bit nse;
        case core.CurrentSecurityState() of
            when SS_Secure
                ns = '0';
                nse = '0';
            when SS_NonSecure
                ns = '1';
                nse = '0';
            when SS_Realm
                ns = '1';
                nse = '1';
            otherwise core.Unreachable();
        SPESamplePreviousBranchAddress = core.SetBit(SPESamplePreviousBranchAddress,63,ns)
        SPESamplePreviousBranchAddress = core.SetBit(SPESamplePreviousBranchAddress,60,nse)
        SPESamplePreviousBranchAddress = core.SetField(SPESamplePreviousBranchAddress,62,61,core.APSR.EL);
        SPESamplePreviousBranchAddressValid = True;
    if not core.StatisticalProfilingEnabled():
        if taken_flag:
            # Invalidate previous branch address, if profiling is disabled
            # or prohibited.
            SPESamplePreviousBranchAddressValid = False;
        return;
    if SPESampleInFlight:
        is_direct = branch_type IN {'DIR', 'DIRCALL'};
        SPESampleClass = '10';
        SPESampleSubclass = core.SetBit(SPESampleSubclass,1,'0' if is_direct else '1')
        SPESampleSubclass = core.SetBit(SPESampleSubclass,0,'1' if conditional else '0')
        SPESampleOpType = OpType_Branch;
        # Save the target address.
        if taken_flag:
            SPESampleAddress[SPEAddrPosBranchTarget] = core.SetField(SPESampleAddress[SPEAddrPosBranchTarget],55,0,core.Field(target,55,0));
            bit ns;
            bit nse;
            case core.CurrentSecurityState() of
                when SS_Secure
                    ns = '0';
                    nse = '0';
                when SS_NonSecure
                    ns = '1';
                    nse = '0';
                when SS_Realm
                    ns = '1';
                    nse = '1';
                otherwise core.Unreachable();
            SPESampleAddress[SPEAddrPosBranchTarget]<63> = ns;
            SPESampleAddress[SPEAddrPosBranchTarget]<60> = nse;
            SPESampleAddress[SPEAddrPosBranchTarget] = core.SetField(SPESampleAddress[SPEAddrPosBranchTarget],62,61,core.APSR.EL);
            SPESampleAddressValid[SPEAddrPosBranchTarget] = True;
        SPESampleEvents = core.SetBit(SPESampleEvents,6,'1' if not taken_flag else '0')
# core.BranchTo()
# ==========
# Set program counter to a new address, with a branch type1.
# Parameter branch_conditional indicates whether the executed branch has a conditional encoding.
# In AArch64 state the address might include a tag in the top eight bits.
core.BranchTo(core.bits(N) target, BranchType branch_type, boolean branch_conditional)
    core.Hint_Branch(branch_type);
    if N == 32:
        assert core.UsingAArch32();
        _PC = core.ZeroExtend(target, 64);
    else:
        assert N == 64 and not core.UsingAArch32();
        core.bits(64) target_vaddress = AArch64.core.BranchAddr(core.Field(target,63,0), core.APSR.EL);
        if (core.HaveBRBExt() and
            branch_type IN {'DIR', 'INDIR',
                            'DIRCALL', 'INDCALL',
                            'RET'}) then
            core.BRBEBranch(branch_type, branch_conditional, target_vaddress);
        boolean branch_taken = True;
        if core.HaveStatisticalProfiling():
            core.SPEBranch(target, branch_type, branch_conditional, branch_taken);
        _PC = target_vaddress;
    return;
# core.HaveExtendedECDebugEvents()
# ===========================
boolean core.HaveExtendedECDebugEvents()
    return core.IsFeatureImplemented(FEAT_Debugv8p2);
# core.Havev8p8Debug()
# ===============
# Returns True if support for the Debugv8p8 feature is implemented and False otherwise.
boolean core.Havev8p8Debug()
    return core.IsFeatureImplemented(FEAT_Debugv8p8);
# core.CheckExceptionCatch()
# =====================
# Check whether an Exception Catch debug event is set on the current Exception level
core.CheckExceptionCatch(boolean exception_entry)
    # Called after an exception entry or exit, that is, such that the Security state
    # and core.APSR.EL are correct for the exception target. When FEAT_Debugv8p2
    # is not implemented, this function might also be called at any time.
    ss = core.SecurityStateAtEL(core.APSR.EL);
    base = 0;
    case ss of
        when SS_Secure    base = 0;
        when SS_NonSecure base = 4;
        when SS_Realm     base = 16;
        when SS_Root      base = 0;
    if core.HaltingAllowed():
        halt = False;
        if core.HaveExtendedECDebugEvents():
            exception_exit = not exception_entry;
            increment = 4 if ss == SS_Realm else 8;
            ctrl = EDECCR<core.UInt(core.APSR.EL) + base + increment>:EDECCR<core.UInt(core.APSR.EL) + base>;
            case ctrl of
                when '00'  halt = False;
                when '01'  halt = True;
                when '10'  halt = (exception_exit == True);
                when '11'  halt = (exception_entry == True);
        else:
            halt = (EDECCR<core.UInt(core.APSR.EL) + base> == '1');
        if halt:
            if core.Havev8p8Debug() and exception_entry:
                EDESR.EC = '1';
            else:
                core.Halt(DebugHalt_ExceptionCatch);
# core.EnterHypMode()
# ======================
# Take an exception to Hyp mode.
core.EnterHypMode(ExceptionRecord exception, core.bits(32) preferred_exception_return,
                     integer vect_offset)
    core.SynchronizeContext();
    assert core.HaveEL(EL2) and core.CurrentSecurityState() == SS_NonSecure and core.ELUsingAArch32(EL2);
    if core.Halted():
        core.EnterHypModeInDebugState(exception);
        return;
    core.bits(32) spsr = core.GetPSRFromcore.APSR(AArch32_NonDebugState, 32);
    if not (exception.exceptype IN {Exception_IRQ, Exception_FIQ}):
        core.ReportHypEntry(exception);
    core.WriteMode(M32_Hyp);
    SPSR[] = spsr;
    ELR_hyp = preferred_exception_return;
    core.APSR.T = HSCTLR.TE;                       # core.APSR.J is RES0
    core.APSR.SS = '0';
    if not core.HaveEL(EL3) or SCR_GEN[].EA == '0':
         core.APSR.A = '1';
    if not core.HaveEL(EL3) or SCR_GEN[].IRQ == '0':
         core.APSR.I = '1';
    if not core.HaveEL(EL3) or SCR_GEN[].FIQ == '0':
         core.APSR.F = '1';
    core.APSR.E = HSCTLR.EE;
    core.APSR.IL = '0';
    core.APSR.IT = '00000000';
    if core.HaveSSBSExt():
         core.APSR.SSBS = HSCTLR.DSSBS;
    boolean branch_conditional = False;
    core.BranchTo(core.Field(HVBAR,31,5):core.Field(vect_offset,4,0), 'EXCEPTION', branch_conditional);
    core.CheckExceptionCatch(True);                  # Check for debug event on exception entry
    core.EndOfInstruction();
# InstrSet
# ========
enumeration InstrSet {InstrSet_A64, InstrSet_A32, InstrSet_T32};
# core.CurrentInstrSet()
# =================
InstrSet core.CurrentInstrSet()
    InstrSet result;
    if core.UsingAArch32():
        result = InstrSet_A32 if core.APSR.T == '0' else InstrSet_T32;
        # core.APSR.J is RES0. Implementation of T32EE or Jazelle state not permitted.
    else:
        result = InstrSet_A64;
    return result;
SP_mon = 0;
LR_mon = 0;
# core.RBankSelect()
# =============
integer core.RBankSelect(core.bits(5) mode, integer usr, integer fiq, integer irq,
                    integer svc, integer abt, integer und, integer hyp)
    result = 0;
    case mode of
        when M32_User    result = usr;  # User mode
        when M32_FIQ     result = fiq;  # FIQ mode
        when M32_IRQ     result = irq;  # IRQ mode
        when M32_Svc     result = svc;  # Supervisor mode
        when M32_Abort   result = abt;  # Abort mode
        when M32_Hyp     result = hyp;  # Hyp mode
        when M32_Undef   result = und;  # Undefined mode
        when M32_System  result = usr;  # System mode uses User mode registers
        otherwise        core.Unreachable(); # Monitor mode
    return result;
# core.LookUpRIndex()
# ==============
integer core.LookUpRIndex(integer n, core.bits(5) mode)
    assert n >= 0 and n <= 14;
    result = 0;
    case n of  # Select  index by mode:     usr fiq irq svc abt und hyp
        when 8     result = core.RBankSelect(mode,  8, 24,  8,  8,  8,  8,  8);
        when 9     result = core.RBankSelect(mode,  9, 25,  9,  9,  9,  9,  9);
        when 10    result = core.RBankSelect(mode, 10, 26, 10, 10, 10, 10, 10);
        when 11    result = core.RBankSelect(mode, 11, 27, 11, 11, 11, 11, 11);
        when 12    result = core.RBankSelect(mode, 12, 28, 12, 12, 12, 12, 12);
        when 13    result = core.RBankSelect(mode, 13, 29, 17, 19, 21, 23, 15);
        when 14    result = core.RBankSelect(mode, 14, 30, 16, 18, 20, 22, 14);
        otherwise  result = n;
    return result;
# Rmode[] - non-assignment form
# =============================
core.bits(32) Rmode[integer n, core.bits(5) mode]
    assert n >= 0 and n <= 14;
    # Check for attempted use of Monitor mode in Non-secure state.
    if core.CurrentSecurityState() != SS_Secure:
         assert mode != M32_Monitor;
    assert not core.BadMode(mode);
    if mode == M32_Monitor:
        if n == 13: return SP_mon;
        elsif n == 14:
     return LR_mon;
        else return core.Field(_core.readR(n),31,0);
    else:
        return _core.R[core.LookUpRIndex(n, mode)core.Field(],31,0);
# Rmode[] - assignment form
# =========================
Rmode[integer n, core.bits(5) mode] = core.bits(32) value
    assert n >= 0 and n <= 14;
    # Check for attempted use of Monitor mode in Non-secure state.
    if core.CurrentSecurityState() != SS_Secure:
         assert mode != M32_Monitor;
    assert not core.BadMode(mode);
    if mode == M32_Monitor:
        if n == 13: SP_mon = value;
        elsif n == 14:
     LR_mon = value;
        else _core.R[n] = core.SetField(_core.readR(n),31,0,value);
    else:
        # It is CONSTRAINED raise Exception('UNPREDICTABLE') whether the upper 32 bits of the X
        # register are unchanged or set to zero. This is also tested for on
        # exception entry, as this applies to all AArch32 registers.
        if core.HaveAArch64() and core.ConstrainUnpredictableBool(Unpredictable_ZEROUPPER):
            _core.R[core.LookUpRIndex(n, mode)] = core.ZeroExtend(value, 64);
        else:
            _core.R[core.LookUpRIndex(n, mode)] = core.SetField(mode)],31,0,value);
    return;
# R[] - assignment form
# =====================
core.R[integer n] = core.bits(32) value
    Rmode[n, core.APSR.M] = value;
    return;
# R[] - non-assignment form
# =========================
core.bits(32) core.R[integer n]
    if n == 15:
        offset = (8 if core.CurrentInstrSet() == InstrSet_A32 else 4);
        return core.Field(_PC,31,0) + offset;
    else:
        return Rmode[n, core.APSR.M];
# core.EnterModeInDebugState()
# ===============================
# Take an exception in Debug state to a mode other than Monitor and Hyp mode.
core.EnterModeInDebugState(core.bits(5) target_mode)
    core.SynchronizeContext();
    assert core.ELUsingAArch32(EL1) and core.APSR.EL != EL2;
    if core.APSR.M == M32_Monitor:
         SCR.NS = '0';
    core.WriteMode(target_mode);
    SPSR[] = UNKNOWN = 0;
    core.R[14] = UNKNOWN = 0;
    # In Debug state, the PE always execute T32 instructions when in AArch32 state, and
    # core.APSR.{SS,A,I,F} are not observable so behave as UNKNOWN.
    core.APSR.T = '1';                             # core.APSR.J is RES0
    core.APSR.<SS,A,I,F> = UNKNOWN = 0;
    DLR = UNKNOWN = 0;
    DSPSR = UNKNOWN = 0;
    core.APSR.E = SCTLR.EE;
    core.APSR.IL = '0';
    core.APSR.IT = '00000000';
    if core.HavePANExt() and SCTLR.SPAN == '0':
         core.APSR.PAN = '1';
    if core.HaveSSBSExt():
         core.APSR.SSBS = bit UNKNOWN;
    EDSCR.ERR = '1';
    core.UpdateEDSCRFields();                        # Update EDSCR processor state flags.
    core.EndOfInstruction();
# core.ExcVectorBase()
# ===============
core.bits(32) core.ExcVectorBase()
    if SCTLR.V == '1':
          # Hivecs selected, base = 0xFFFF0000
        return core.Ones(16):core.Zeros(16);
    else:
        return core.Field(VBAR,31,5):core.Zeros(5);
# core.EnterMode()
# ===================
# Take an exception to a mode other than Monitor and Hyp mode.
core.EnterMode(core.bits(5) target_mode, core.bits(32) preferred_exception_return, integer lr_offset,
                  integer vect_offset)
    core.SynchronizeContext();
    assert core.ELUsingAArch32(EL1) and core.APSR.EL != EL2;
    if core.Halted():
        core.EnterModeInDebugState(target_mode);
        return;
    core.bits(32) spsr = core.GetPSRFromcore.APSR(AArch32_NonDebugState, 32);
    if core.APSR.M == M32_Monitor:
         SCR.NS = '0';
    core.WriteMode(target_mode);
    SPSR[] = spsr;
    core.R[14] = preferred_exception_return + lr_offset;
    core.APSR.T = SCTLR.TE;                        # core.APSR.J is RES0
    core.APSR.SS = '0';
    if target_mode == M32_FIQ:
        core.APSR.<A,I,F> = '111';
    elsif target_mode IN {M32_Abort, M32_IRQ}:
        core.APSR.<A,I> = '11';
    else:
        core.APSR.I = '1';
    core.APSR.E = SCTLR.EE;
    core.APSR.IL = '0';
    core.APSR.IT = '00000000';
    if core.HavePANExt() and SCTLR.SPAN == '0':
         core.APSR.PAN = '1';
    if core.HaveSSBSExt():
         core.APSR.SSBS = SCTLR.DSSBS;
    boolean branch_conditional = False;
    core.BranchTo(core.ExcVectorBase()<31:5>:core.Field(vect_offset,4,0), 'EXCEPTION', branch_conditional);
    core.CheckExceptionCatch(True);                  # Check for debug event on exception entry
    core.EndOfInstruction();
# core.LSL_C()
# =======
(core.bits(N), bit) core.LSL_C(core.bits(N) x, integer shift)
    assert shift > 0 and shift < 256;
    extended_x = x : core.Zeros(shift);
    result = extended_x<N-1:0>;
    carry_out = extended_x<N>;
    return (result, carry_out);
# core.LSL()
# =====
core.bits(N) core.LSL(core.bits(N) x, integer shift)
    assert shift >= 0;
    core.bits(N) result;
    if shift == 0:
        result = x;
    else:
        (result, -) = core.LSL_C(x, shift);
    return result;
# core.ITAdvance()
# ===================
core.ITAdvance()
    if core.Field(core.APSR.IT,2,0) == '000':
        core.APSR.IT = '00000000';
    else:
        core.APSR.IT = core.SetField(core.APSR.IT,4,0,core.LSL(core.Field(core.APSR.IT,4,0), 1));
    return;
# core.ExceptionSyndrome()
# ===================
# Return a blank exception syndrome record for an exception of the given type1.
ExceptionRecord core.ExceptionSyndrome(Exception exceptype)
    ExceptionRecord r;
    r.exceptype = exceptype;
    # Initialize all other fields
    r.syndrome  = core.Zeros(25);
    r.syndrome2 = core.Zeros(24);
    r.vaddress  = core.Zeros(64);
    r.ipavalid  = False;
    r.NS        = '0';
    r.ipaddress = core.Zeros(56);
    r.paddress.paspace = PASpace UNKNOWN;
    r.paddress.address = UNKNOWN = 0;
    r.trappedsyscallinst = False;
    return r;
# core.NextInstrAddr()
# ===============
# Return address of the sequentially next instruction.
core.bits(N) core.NextInstrAddr(integer N);
# core.DebugTargetFrom()
# =================
core.bits(2) core.DebugTargetFrom(SecurityState from_state)
    route_to_el2 = False;
    if core.HaveEL(EL2) and (from_state != SS_Secure or
        (core.HaveSecureEL2Ext() and (not core.HaveEL(EL3) or SCR_EL3.EEL2 == '1'))) then
        if core.ELUsingAArch32(EL2):
            route_to_el2 = (HDCR.TDE == '1' or HCR.TGE == '1');
        else:
            route_to_el2 = (MDCR_EL2.TDE == '1' or HCR_EL2.TGE == '1');
    else:
        route_to_el2 = False;
    target = 0;
    if route_to_el2:
        target = EL2;
    elsif core.HaveEL(EL3) and not core.HaveAArch64() and from_state == SS_Secure:
        target = EL3;
    else:
        target = EL1;
    return target;
# core.DebugTarget()
# =============
# Returns the debug exception target Exception level
core.bits(2) core.DebugTarget()
    ss = core.CurrentSecurityState();
    return core.DebugTargetFrom(ss);
# core.SSAdvance()
# ===========
# Advance the Software Step state machine.
core.SSAdvance()
    # A simpler implementation of this function just clears core.APSR.SS to zero regardless of the
    # current Software Step state machine. However, this check is made to illustrate that the
    # processor only needs to consider advancing the state machine from the active-not-pending
    # state.
    target = core.DebugTarget();
    step_enabled = not core.ELUsingAArch32(target) and MDSCR_EL1.SS == '1';
    active_not_pending = step_enabled and core.APSR.SS == '1';
    if active_not_pending:
         core.APSR.SS = '0';
    return;
# core.TakeSVCException()
# ==========================
core.TakeSVCException(core.bits(16) immediate)
    core.ITAdvance();
    core.SSAdvance();
    route_to_hyp = core.APSR.EL == EL0 and core.EL2Enabled() and HCR.TGE == '1';
    core.bits(32) preferred_exception_return = core.NextInstrAddr(32);
    vect_offset = 0x08;
    lr_offset = 0;
    if core.APSR.EL == EL2 or route_to_hyp:
        exception = core.ExceptionSyndrome(Exception_SupervisorCall);
        exception.syndrome = core.SetField(exception.syndrome,15,0,immediate);
        if core.APSR.EL == EL2:
            core.EnterHypMode(exception, preferred_exception_return, vect_offset);
        else:
            core.EnterHypMode(exception, preferred_exception_return, 0x14);
    else:
        core.EnterMode(M32_Svc, preferred_exception_return, lr_offset, vect_offset);
# AArch64.core.MaybeZeroRegisterUppers()
# =================================
# On taking an exception to  AArch64 from AArch32, it is CONSTRAINED raise Exception('UNPREDICTABLE') whether the top
# 32 bits of registers visible at any lower Exception level using AArch32 are set to zero.
AArch64.core.MaybeZeroRegisterUppers()
    assert core.UsingAArch32();         # Always called from AArch32 state before entering AArch64 state
    first = 0;
    last = 0;
    include_R15 = False;
    if core.APSR.EL == EL0 and not core.ELUsingAArch32(EL1):
        first = 0;  last = 14;  include_R15 = False;
    elsif core.APSR.EL IN {EL0, EL1} and core.EL2Enabled() and not core.ELUsingAArch32(EL2):
        first = 0;  last = 30;  include_R15 = False;
    else:
        first = 0;  last = 30;  include_R15 = True;
    for n = first to last
        if (n != 15 or include_R15) and core.ConstrainUnpredictableBool(Unpredictable_ZEROUPPER):
            _core.R[n] = core.SetField(_core.readR(n),63,32,core.Zeros(32));
    return;
# AArch64.core.ExceptionClass()
# ========================
# Returns the Exception Class and Instruction Length fields to be reported in ESR
(integer,bit) AArch64.core.ExceptionClass(Exception exceptype, core.bits(2) target_el)
    il_is_valid = True;
    from_32 = core.UsingAArch32();
    ec = 0;
    case exceptype of
        when Exception_Uncategorized         ec = 0x00; il_is_valid = False;
        when Exception_WFxTrap               ec = 0x01;
        when Exception_CP15RTTrap            ec = 0x03; assert from_32;
        when Exception_CP15RRTTrap           ec = 0x04; assert from_32;
        when Exception_CP14RTTrap            ec = 0x05; assert from_32;
        when Exception_CP14DTTrap            ec = 0x06; assert from_32;
        when Exception_AdvSIMDFPAccessTrap   ec = 0x07;
        when Exception_FPIDTrap              ec = 0x08;
        when Exception_PACTrap               ec = 0x09;
        when Exception_LDST64BTrap           ec = 0x0A;
        when Exception_TSTARTAccessTrap      ec = 0x1B;
        when Exception_GPC                   ec = 0x1E;
        when Exception_CP14RRTTrap           ec = 0x0C; assert from_32;
        when Exception_BranchTarget          ec = 0x0D;
        when Exception_IllegalState          ec = 0x0E; il_is_valid = False;
        when Exception_SupervisorCall        ec = 0x11;
        when Exception_HypervisorCall        ec = 0x12;
        when Exception_MonitorCall           ec = 0x13;
        when Exception_SystemRegisterTrap    ec = 0x18; assert not from_32;
        when Exception_SystemRegister128Trap ec = 0x14; assert not from_32;
        when Exception_SVEAccessTrap         ec = 0x19; assert not from_32;
        when Exception_ERetTrap              ec = 0x1A; assert not from_32;
        when Exception_PACFail               ec = 0x1C; assert not from_32;
        when Exception_SMEAccessTrap         ec = 0x1D; assert not from_32;
        when Exception_InstructionAbort      ec = 0x20; il_is_valid = False;
        when Exception_PCAlignment           ec = 0x22; il_is_valid = False;
        when Exception_DataAbort             ec = 0x24;
        when Exception_NV2DataAbort          ec = 0x25;
        when Exception_SPAlignment           ec = 0x26; il_is_valid = False; assert not from_32;
        when Exception_MemCpyMemSet          ec = 0x27;
        when Exception_GCSFail               ec = 0x2D; assert not from_32;
        when Exception_FPTrappedException    ec = 0x28;
        when Exception_SError                ec = 0x2F; il_is_valid = False;
        when Exception_Breakpoint            ec = 0x30; il_is_valid = False;
        when Exception_SoftwareStep          ec = 0x32; il_is_valid = False;
        when Exception_Watchpoint            ec = 0x34; il_is_valid = False;
        when Exception_NV2Watchpoint         ec = 0x35; il_is_valid = False;
        when Exception_SoftwareBreakpoint    ec = 0x38;
        when Exception_VectorCatch           ec = 0x3A; il_is_valid = False; assert from_32;
        otherwise                            core.Unreachable();
    if ec IN {0x20,0x24,0x30,0x32,0x34} and target_el == core.APSR.EL:
        ec = ec + 1;
    if ec IN {0x11,0x12,0x13,0x28,0x38} and not from_32:
        ec = ec + 4;
    bit il;
    if il_is_valid:
        il = '1' if core.ThisInstrLength() == 32 else '0';
    else:
        il = '1';
    assert from_32 or il == '1';            # AArch64 instructions always 32-bit
    return (ec,il);
type ESRType;
# ESR[] - non-assignment form
# ===========================
ESRType EScore.R[core.bits(2) regime]
    r = 0;
    case regime of
        when EL1  r = ESR_EL1;
        when EL2  r = ESR_EL2;
        when EL3  r = ESR_EL3;
        otherwise core.Unreachable();
    return r;
# ESR[] - non-assignment form
# ===========================
ESRType ESR[]
    return EScore.R[core.S1TranslationRegime()];
# ESR[] - assignment form
# =======================
EScore.R[core.bits(2) regime] = ESRType value
    core.bits(64) r = value;
    case regime of
        when EL1  ESR_EL1 = r;
        when EL2  ESR_EL2 = r;
        when EL3  ESR_EL3 = r;
        otherwise core.Unreachable();
    return;
# ESR[] - assignment form
# =======================
ESR[] = ESRType value
    EScore.R[core.S1TranslationRegime()] = value; log.info(f'Setting R{core.S1TranslationRegime()}={hex(core.UInt(core.Field(value)))}')
# FAR[] - non-assignment form
# ===========================
core.bits(64) FAcore.R[core.bits(2) regime]
    r = 0;
    case regime of
        when EL1  r = FAR_EL1;
        when EL2  r = FAR_EL2;
        when EL3  r = FAR_EL3;
        otherwise core.Unreachable();
    return r;
# FAR[] - non-assignment form
# ===========================
core.bits(64) FAR[]
    return FAcore.R[core.S1TranslationRegime()];
# FAR[] - assignment form
# =======================
FAcore.R[core.bits(2) regime] = core.bits(64) value
    core.bits(64) r = value;
    case regime of
        when EL1  FAR_EL1 = r;
        when EL2  FAR_EL2 = r;
        when EL3  FAR_EL3 = r;
        otherwise core.Unreachable();
    return;
# FAR[] - assignment form
# =======================
FAR[] = core.bits(64) value
    FAcore.R[core.S1TranslationRegime()] = value; log.info(f'Setting R{core.S1TranslationRegime()}={hex(core.UInt(core.Field(value)))}')
    return;
# AArch64.core.ReportException()
# =========================
# Report syndrome information for exception taken to AArch64 state.
AArch64.core.ReportException(ExceptionRecord exception, core.bits(2) target_el)
    Exception exceptype = exception.exceptype;
    (ec,il) = AArch64.core.ExceptionClass(exceptype, target_el);
    iss  = exception.syndrome;
    iss2 = exception.syndrome2;
    # IL is not valid for Data Abort exceptions without valid instruction syndrome information
    if ec IN {0x24,0x25} and core.Bit(iss,24) == '0':
        il = '1';
    EScore.R[target_el] = (core.Zeros(8)  :   # <63:56>
                      iss2      :   # <55:32>
                      core.Field(ec,5,0)   :   # <31:26>
                      il        :   # <25>
                      iss);         # <24:0>
    if exceptype IN {
        Exception_InstructionAbort,
        Exception_PCAlignment,
        Exception_DataAbort,
        Exception_NV2DataAbort,
        Exception_NV2Watchpoint,
        Exception_GPC,
        Exception_Watchpoint
    } then
        FAcore.R[target_el] = exception.vaddress;
    else:
        FAcore.R[target_el] = UNKNOWN = 0;
    if exception.ipavalid:
        HPFAR_EL2 = core.SetField(HPFAR_EL2,47,4,core.Field(exception.ipaddress,55,12));
        if core.IsSecureEL2Enabled() and core.CurrentSecurityState() == SS_Secure:
            HPFAR_EL2.NS = exception.NS;
        else:
            HPFAR_EL2.NS = '0';
    elsif target_el == EL2:
        HPFAR_EL2 = core.SetField(HPFAR_EL2,47,4,UNKNOWN = 0);
    if exception.pavalid:
        MFAR_EL3.FPA = core.ZeroExtend(exception.paddress.address<AArch64.core.PAMax()-1:12>, 44);
        case exception.paddress.paspace of
            when PAS_Secure     MFAR_EL3.<NSE,NS> = '00';
            when PAS_NonSecure  MFAR_EL3.<NSE,NS> = '01';
            when PAS_Root       MFAR_EL3.<NSE,NS> = '10';
            when PAS_Realm      MFAR_EL3.<NSE,NS> = '11';
    return;
# ELR[] - non-assignment form
# ===========================
core.bits(64) ELcore.R[core.bits(2) el]
    r = 0;
    case el of
        when EL1  r = ELR_EL1;
        when EL2  r = ELR_EL2;
        when EL3  r = ELR_EL3;
        otherwise core.Unreachable();
    return r;
# ELR[] - non-assignment form
# ===========================
core.bits(64) ELR[]
    assert core.APSR.EL != EL0;
    return ELcore.R[core.APSR.EL];
# ELR[] - assignment form
# =======================
ELcore.R[core.bits(2) el] = core.bits(64) value
    core.bits(64) r = value;
    case el of
        when EL1  ELR_EL1 = r;
        when EL2  ELR_EL2 = r;
        when EL3  ELR_EL3 = r;
        otherwise core.Unreachable();
    return;
# ELR[] - assignment form
# =======================
ELR[] = core.bits(64) value
    assert core.APSR.EL != EL0;
    ELcore.R[core.APSR.EL] = value; log.info(f'Setting R{core.APSR.EL}={hex(core.UInt(core.Field(value)))}')
    return;
# core.HaveDoubleFaultExt()
# ====================
boolean core.HaveDoubleFaultExt()
    return core.IsFeatureImplemented(FEAT_DoubleFault);
# core.HaveIESB()
# ==========
boolean core.HaveIESB()
    return core.IsFeatureImplemented(FEAT_IESB);
# System Registers
# ================
array core.bits(MAX_VL) _ZA[0..255];
# core.MaybeZeroSVEUppers()
# ====================
core.MaybeZeroSVEUppers(core.bits(2) target_el)
    lower_enabled = False;
    if core.UInt(target_el) <= core.UInt(core.APSR.EL) or not core.IsSVEEnabled(target_el):
        return;
    if target_el == EL3:
        if core.EL2Enabled():
            lower_enabled = core.IsFPEnabled(EL2);
        else:
            lower_enabled = core.IsFPEnabled(EL1);
    elsif target_el == EL2:
        assert not core.ELUsingAArch32(EL2);
        if HCR_EL2.TGE == '0':
            lower_enabled = core.IsFPEnabled(EL1);
        else:
            lower_enabled = core.IsFPEnabled(EL0);
    else:
        assert target_el == EL1 and not core.ELUsingAArch32(EL1);
        lower_enabled = core.IsFPEnabled(EL0);
    if lower_enabled:
        constant integer VL = CurrentVL if core.IsSVEEnabled(core.APSR.EL) else 128;
        constant integer PL = VL DIV 8;
        for n in range(0,31+1):
            if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
                _Z[n] = core.ZeroExtend(_Z[n]<VL-1:0>, MAX_VL);
        for n in range(0,15+1):
            if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
                _P[n] = core.ZeroExtend(_P[n]<PL-1:0>, MAX_PL);
        if core.ConstrainUnpredictableBool(Unpredictable_SVEZEROUPPER):
            _FFR = core.ZeroExtend(_FFR<PL-1:0>, MAX_PL);
        if core.HaveSME() and core.APSR.ZA == '1':
            constant integer SVL = CurrentSVL;
            constant integer accessiblevecs = SVL DIV 8;
            constant integer allvecs = core.MaxImplementedSVL() DIV 8;
            for n = 0 to accessiblevecs - 1
                if core.ConstrainUnpredictableBool(Unpredictable_SMEZEROUPPER):
                    _ZA[n] = core.ZeroExtend(_ZA[n]<SVL-1:0>, MAX_VL);
            for n = accessiblevecs to allvecs - 1
                if core.ConstrainUnpredictableBool(Unpredictable_SMEZEROUPPER):
                    _ZA[n] = core.Zeros(MAX_VL);
# core.ResetSVEState()
# ===============
core.ResetSVEState()
    for n in range(0,31+1):
        _Z[n] = core.Zeros(MAX_VL);
    for n in range(0,15+1):
        _P[n] = core.Zeros(MAX_PL);
    _FFR = core.Zeros(MAX_PL);
    FPSR = core.ZeroExtend(core.Field(0x0800009f,31,0), 64);
type SCTLRType;
# SCTLR[] - non-assignment form
# =============================
SCTLRType SCTLcore.R[core.bits(2) regime]
    r = 0;
    case regime of
        when EL1  r = SCTLR_EL1;
        when EL2  r = SCTLR_EL2;
        when EL3  r = SCTLR_EL3;
        otherwise core.Unreachable();
    return r;
# SCTLR[] - non-assignment form
# =============================
SCTLRType SCTLR[]
    return SCTLcore.R[core.S1TranslationRegime()];
# core.SynchronizeErrors()
# ===================
# Implements the error synchronization event.
core.SynchronizeErrors();
# AArch64.core.TakeExceptionInDebugState()
# ===================================
# Take an exception in Debug state to an Exception level using AArch64.
AArch64.core.TakeExceptionInDebugState(core.bits(2) target_el, ExceptionRecord exception_in)
    assert core.HaveEL(target_el) and not core.ELUsingAArch32(target_el) and core.UInt(target_el) >= core.UInt(core.APSR.EL);
    assert target_el != EL3 or EDSCR.SDD == '0';
    ExceptionRecord exception = exception_in;
    sync_errors = False;
    iesb_req = False;
    if core.HaveIESB():
        sync_errors = SCTLcore.R[target_el].IESB == '1';
        if core.HaveDoubleFaultExt():
            sync_errors = sync_errors or (SCR_EL3.<EA,NMEA> == '11' and target_el == EL3);
        # SCTLR[].IESB and/or SCR_EL3.NMEA (if applicable) might be ignored in Debug state.
        if not core.ConstrainUnpredictableBool(Unpredictable_IESBinDebug):
            sync_errors = False;
    else:
        sync_errors = False;
    if core.HaveTME() and TSTATE.depth > 0:
        TMFailure cause;
        case exception.exceptype of
            when Exception_SoftwareBreakpoint cause = TMFailure_DBG;
            when Exception_Breakpoint         cause = TMFailure_DBG;
            when Exception_Watchpoint         cause = TMFailure_DBG;
            when Exception_SoftwareStep       cause = TMFailure_DBG;
            otherwise                         cause = TMFailure_ERR;
        core.FailTransaction(cause, False);
    core.SynchronizeContext();
    # If coming from AArch32 state, the top parts of the X[] registers might be set to zero
    from_32 = core.UsingAArch32();
    if from_32:
         AArch64.core.MaybeZeroRegisterUppers();
    if from_32 and core.HaveSME() and core.APSR.SM == '1':
        core.ResetSVEState();
    else:
        core.MaybeZeroSVEUppers(target_el);
    AArch64.core.ReportException(exception, target_el);
    core.APSR.EXLOCK = '0';  # Effective value of GCSCR_ELx.EXLOCKEN is 0 in Debug state
    core.APSR.EL = target_el;
    core.APSR.nRW = '0';
    core.APSR.SP = '1';
    SPSR[] = UNKNOWN = 0;
    ELR[] = UNKNOWN = 0;
    # core.APSR.{SS,D,A,I,F} are not observable and ignored in Debug state, so behave as if UNKNOWN.
    core.APSR.<SS,D,A,I,F> = UNKNOWN = 0;
    core.APSR.IL = '0';
    if from_32:
                                     # Coming from AArch32
        core.APSR.IT = '00000000';
        core.APSR.T = '0';                         # core.APSR.J is RES0
    if (core.HavePANExt() and (core.APSR.EL == EL1 or (core.APSR.EL == EL2 and core.ELIsInHost(EL0))) and
        SCTLR[].SPAN == '0') then
        core.APSR.PAN = '1';
    if core.HaveUAOExt():
         core.APSR.UAO = '0';
    if core.HaveBTIExt():
         core.APSR.BTYPE = '00';
    if core.HaveSSBSExt():
         core.APSR.SSBS = bit UNKNOWN;
    if core.HaveMTEExt():
         core.APSR.TCO = '1';
    DLR_EL0 = UNKNOWN = 0;
    DSPSR_EL0 = UNKNOWN = 0;
    EDSCR.ERR = '1';
    core.UpdateEDSCRFields();                        # Update EDSCR processor state flags.
    if sync_errors:
        core.SynchronizeErrors();
    core.EndOfInstruction();
# core.BRBEException()
# ===============
# Called to write exception branch record when BRB is active.
core.BRBEException(ExceptionRecord erec, core.bits(64) preferred_exception_return,
              core.bits(64) target_address_in, core.bits(2) target_el, boolean trappedsyscallinst)
    core.bits(64) target_address = target_address_in;
    Exception exception = erec.exceptype;
    core.bits(25) iss = erec.syndrome;
    case target_el of
        when EL3  if not core.HaveBRBEv1p1() or (MDCR_EL3.E3BREC == MDCR_EL3.E3BREW):
       return;
        when EL2  if BRBCR_EL2.EXCEPTION == '0':
       return;
        when EL1  if BRBCR_EL1.EXCEPTION == '0':
       return;
    boolean source_valid = core.BranchRecordAllowed(core.APSR.EL);
    boolean target_valid = core.BranchRecordAllowed(target_el);
    if source_valid or target_valid:
        branch_type = 0;
        case exception of
            when Exception_Uncategorized         branch_type = '100011'; # Trap
            when Exception_WFxTrap               branch_type = '100011'; # Trap
            when Exception_CP15RTTrap            branch_type = '100011'; # Trap
            when Exception_CP15RRTTrap           branch_type = '100011'; # Trap
            when Exception_CP14RTTrap            branch_type = '100011'; # Trap
            when Exception_CP14DTTrap            branch_type = '100011'; # Trap
            when Exception_AdvSIMDFPAccessTrap   branch_type = '100011'; # Trap
            when Exception_FPIDTrap              branch_type = '100011'; # Trap
            when Exception_PACTrap               branch_type = '100011'; # Trap
            when Exception_TSTARTAccessTrap      branch_type = '100011'; # Trap
            when Exception_CP14RRTTrap           branch_type = '100011'; # Trap
            when Exception_BranchTarget          branch_type = '101011'; # Inst Fault
            when Exception_IllegalState          branch_type = '100011'; # Trap
            when Exception_SupervisorCall
                if not trappedsyscallinst:
                          branch_type = '100010'; # Call
                else                             branch_type = '100011'; # Trap
            when Exception_HypervisorCall        branch_type = '100010'; # Call
            when Exception_MonitorCall
                if not trappedsyscallinst:
                          branch_type = '100010'; # Call
                else                             branch_type = '100011'; # Trap
            when Exception_SystemRegisterTrap    branch_type = '100011'; # Trap
            when Exception_SystemRegister128Trap branch_type = '100011'; # Trap
            when Exception_SVEAccessTrap         branch_type = '100011'; # Trap
            when Exception_SMEAccessTrap         branch_type = '100011'; # Trap
            when Exception_ERetTrap              branch_type = '100011'; # Trap
            when Exception_PACFail               branch_type = '101100'; # Data Fault
            when Exception_InstructionAbort      branch_type = '101011'; # Inst Fault
            when Exception_PCAlignment           branch_type = '101010'; # Alignment
            when Exception_DataAbort             branch_type = '101100'; # Data Fault
            when Exception_NV2DataAbort          branch_type = '101100'; # Data Fault
            when Exception_SPAlignment           branch_type = '101010'; # Alignment
            when Exception_FPTrappedException    branch_type = '100011'; # Trap
            when Exception_SError                branch_type = '100100'; # System Error
            when Exception_Breakpoint            branch_type = '100110'; # Inst debug
            when Exception_SoftwareStep          branch_type = '100110'; # Inst debug
            when Exception_Watchpoint            branch_type = '100111'; # Data debug
            when Exception_NV2Watchpoint         branch_type = '100111'; # Data debug
            when Exception_SoftwareBreakpoint    branch_type = '100110'; # Inst debug
            when Exception_IRQ                   branch_type = '101110'; # IRQ
            when Exception_FIQ                   branch_type = '101111'; # FIQ
            when Exception_MemCpyMemSet          branch_type = '100011'; # Trap
            when Exception_GCSFail
                if core.Field(iss,23,20) == '0000':
                         branch_type = '101100'; # Data Fault
                elsif core.Field(iss,23,20) == '0001':
      branch_type = '101011'; # Inst Fault
                elsif core.Field(iss,23,20) == '0010':
      branch_type = '100011'; # Trap
                else                             core.Unreachable();
            otherwise                            core.Unreachable();
        bit ccu;
        cc = 0;
        (ccu, cc) = core.BranchEncCycleCount();
        bit lastfailed = BRBFCR_EL1.LASTFAILED if core.HaveTME() else '0';
        bit transactional = '1' if source_valid and core.HaveTME() and TSTATE.depth > 0 else '0';
        core.bits(2) el = target_el if target_valid else '00';
        bit mispredict = '0';
        bit sv = '1' if source_valid else '0';
        bit tv = '1' if target_valid else '0';
        core.bits(64) source_address = preferred_exception_return if source_valid else core.Zeros(64);
        if not target_valid:
            target_address = core.Zeros(64);
        else:
            target_address = AArch64.core.BranchAddr(target_address, target_el);
        core.UpdateBranchRecordBuffer(ccu, cc, lastfailed, transactional, branch_type, el, mispredict,
                                 sv:tv, source_address, target_address);
        BRBFCR_EL1.LASTFAILED = '0';
        core.PMUEvent(PMU_EVENT_BRB_FILTRATE);
    return;
# core.GetCurrentEXLOCKEN()
# ====================
boolean core.GetCurrentEXLOCKEN()
    case core.APSR.EL of
        when EL0
            core.Unreachable();
        when EL1
            return GCSCR_EL1.EXLOCKEN == '1';
        when EL2
            return GCSCR_EL2.EXLOCKEN == '1';
        when EL3
            return GCSCR_EL3.EXLOCKEN == '1';
# core.HaveNV2Ext()
# ============
# Returns True if Enhanced Nested Virtualization is implemented.
boolean core.HaveNV2Ext()
    return core.IsFeatureImplemented(FEAT_NV2);
# core.HaveNVExt()
# ===========
# Returns True if Nested Virtualization is implemented.
boolean core.HaveNVExt()
    return core.IsFeatureImplemented(FEAT_NV);
# core.InsertIESBBeforeException()
# ===========================
# Returns an implementation defined choice whether to insert an implicit error synchronization
# barrier before exception.
# If SCTLR_ELx.IESB is 1 when an exception is generated to ELx, any pending Unrecoverable
# SError interrupt must be taken before executing any instructions in the exception handler.
# However, this can be before the branch to the exception handler is made.
boolean core.InsertIESBBeforeException(core.bits(2) el)
    return (core.HaveIESB() and boolean IMPLEMENTATION_DEFINED
            "Has Implicit Error Synchronization Barrier before Exception");
# core.TakeUnmaskedPhysicalSErrorInterrupts()
# ======================================
# Take any pending unmasked physical SError interrupt.
core.TakeUnmaskedPhysicalSErrorInterrupts(boolean iesb_req);
# VBAR[] - non-assignment form
# ============================
core.bits(64) VBAcore.R[core.bits(2) regime]
    r = 0;
    case regime of
        when EL1  r = VBAR_EL1;
        when EL2  r = VBAR_EL2;
        when EL3  r = VBAR_EL3;
        otherwise core.Unreachable();
    return r;
# VBAR[] - non-assignment form
# ============================
core.bits(64) VBAR[]
    return VBAcore.R[core.S1TranslationRegime()];
# AArch64.core.TakeException()
# =======================
# Take an exception to an Exception level using AArch64.
AArch64.core.TakeException(core.bits(2) target_el, ExceptionRecord exception_in,
                      core.bits(64) preferred_exception_return, integer vect_offset_in)
    assert core.HaveEL(target_el) and not core.ELUsingAArch32(target_el) and core.UInt(target_el) >= core.UInt(core.APSR.EL);
    if core.Halted():
        AArch64.core.TakeExceptionInDebugState(target_el, exception_in);
        return;
    ExceptionRecord exception = exception_in;
    sync_errors = False;
    iesb_req = False;
    if core.HaveIESB():
        sync_errors = SCTLcore.R[target_el].IESB == '1';
        if core.HaveDoubleFaultExt():
            sync_errors = sync_errors or (SCR_EL3.<EA,NMEA> == '11' and target_el == EL3);
        if sync_errors and core.InsertIESBBeforeException(target_el):
            core.SynchronizeErrors();
            iesb_req = False;
            sync_errors = False;
            core.TakeUnmaskedPhysicalSErrorInterrupts(iesb_req);
    else:
        sync_errors = False;
    if core.HaveTME() and TSTATE.depth > 0:
        TMFailure cause;
        case exception.exceptype of
            when Exception_SoftwareBreakpoint cause = TMFailure_DBG;
            when Exception_Breakpoint         cause = TMFailure_DBG;
            when Exception_Watchpoint         cause = TMFailure_DBG;
            when Exception_SoftwareStep       cause = TMFailure_DBG;
            otherwise                         cause = TMFailure_ERR;
        core.FailTransaction(cause, False);
    core.SynchronizeContext();
    # If coming from AArch32 state, the top parts of the X[] registers might be set to zero
    from_32 = core.UsingAArch32();
    if from_32:
         AArch64.core.MaybeZeroRegisterUppers();
    if from_32 and core.HaveSME() and core.APSR.SM == '1':
        core.ResetSVEState();
    else:
        core.MaybeZeroSVEUppers(target_el);
    integer vect_offset = vect_offset_in;
    if core.UInt(target_el) > core.UInt(core.APSR.EL):
        lower_32 = False;
        if target_el == EL3:
            if core.EL2Enabled():
                lower_32 = core.ELUsingAArch32(EL2);
            else:
                lower_32 = core.ELUsingAArch32(EL1);
        elsif core.IsInHost() and core.APSR.EL == EL0 and target_el == EL2:
            lower_32 = core.ELUsingAArch32(EL0);
        else:
            lower_32 = core.ELUsingAArch32(target_el - 1);
        vect_offset = vect_offset + (0x600 if lower_32 else 0x400);
    elsif core.APSR.SP == '1':
        vect_offset = vect_offset + 0x200;
    core.bits(64) spsr = core.GetPSRFromcore.APSR(AArch64_NonDebugState, 64);
    if core.APSR.EL == EL1 and target_el == EL1 and core.EL2Enabled():
        if core.HaveNV2Ext() and (HCR_EL2.<NV,NV1,NV2> == '100' or HCR_EL2.<NV,NV1,NV2> == '111'):
            spsr = core.SetField(spsr,3,2,'10');
        else:
            if core.HaveNVExt() and HCR_EL2.<NV,NV1> == '10':
                spsr = core.SetField(spsr,3,2,'10');
    if core.HaveBTIExt() and not core.UsingAArch32():
        zero_btype = False;
        # SPSR[].BTYPE is only guaranteed valid for these exception types
        if exception.exceptype IN {Exception_SError, Exception_IRQ, Exception_FIQ,
                              Exception_SoftwareStep, Exception_PCAlignment,
                              Exception_InstructionAbort, Exception_Breakpoint,
                              Exception_VectorCatch, Exception_SoftwareBreakpoint,
                              Exception_IllegalState, Exception_BranchTarget} then
            zero_btype = False;
        else:
            zero_btype = core.ConstrainUnpredictableBool(Unpredictable_ZEROBTYPE);
        if zero_btype:
             spsr = core.SetField(spsr,11,10,'00');
    if core.HaveNV2Ext() and exception.exceptype == Exception_NV2DataAbort and target_el == EL3:
        # External aborts are configured to be taken to EL3
        exception.exceptype = Exception_DataAbort;
    if not (exception.exceptype IN {Exception_IRQ, Exception_FIQ}):
        AArch64.core.ReportException(exception, target_el);
    if core.HaveBRBExt():
        core.BRBEException(exception, preferred_exception_return,
                      core.Field(VBAcore.readR(target_el),63,11):core.Field(vect_offset,10,0), target_el,
                      exception.trappedsyscallinst);
    if core.APSR.EL == target_el:
        if core.GetCurrentEXLOCKEN():
            core.APSR.EXLOCK = '1';
        else:
            core.APSR.EXLOCK = '0';
    else:
        core.APSR.EXLOCK = '0';
    core.APSR.EL = target_el;
    core.APSR.nRW = '0';
    core.APSR.SP = '1';
    SPSR[] = spsr;
    ELR[] = preferred_exception_return;
    core.APSR.SS = '0';
    if core.HaveFeatNMI() and not core.ELUsingAArch32(target_el):
         core.APSR.ALLINT = NOT SCTLR[].SPINTMASK;
    core.APSR.<D,A,I,F> = '1111';
    core.APSR.IL = '0';
    if from_32:
                                     # Coming from AArch32
        core.APSR.IT = '00000000';
        core.APSR.T = '0';                         # core.APSR.J is RES0
    if (core.HavePANExt() and (core.APSR.EL == EL1 or (core.APSR.EL == EL2 and core.ELIsInHost(EL0))) and
        SCTLR[].SPAN == '0') then
        core.APSR.PAN = '1';
    if core.HaveUAOExt():
         core.APSR.UAO = '0';
    if core.HaveBTIExt():
         core.APSR.BTYPE = '00';
    if core.HaveSSBSExt():
         core.APSR.SSBS = SCTLR[].DSSBS;
    if core.HaveMTEExt():
         core.APSR.TCO = '1';
    boolean branch_conditional = False;
    core.BranchTo(core.Field(VBAR[],63,11):core.Field(vect_offset,10,0), 'EXCEPTION', branch_conditional);
    core.CheckExceptionCatch(True);                  # Check for debug event on exception entry
    if sync_errors:
        core.SynchronizeErrors();
        iesb_req = True;
        core.TakeUnmaskedPhysicalSErrorInterrupts(iesb_req);
    core.EndOfInstruction();
# AArch64.core.CallSupervisor()
# ========================
# Calls the Supervisor
AArch64.core.CallSupervisor(core.bits(16) immediate_in)
    core.bits(16) immediate = immediate_in;
    if core.UsingAArch32():
         core.ITAdvance();
    core.SSAdvance();
    route_to_el2 = core.APSR.EL == EL0 and core.EL2Enabled() and HCR_EL2.TGE == '1';
    core.bits(64) preferred_exception_return = core.NextInstrAddr(64);
    vect_offset = 0x0;
    exception = core.ExceptionSyndrome(Exception_SupervisorCall);
    exception.syndrome = core.SetField(exception.syndrome,15,0,immediate);
    if core.UInt(core.APSR.EL) > core.UInt(EL1):
        AArch64.core.TakeException(core.APSR.EL, exception, preferred_exception_return, vect_offset);
    elsif route_to_el2:
        AArch64.core.TakeException(EL2, exception, preferred_exception_return, vect_offset);
    else:
        AArch64.core.TakeException(EL1, exception, preferred_exception_return, vect_offset);
# core.CallSupervisor()
# ========================
# Calls the Supervisor
core.CallSupervisor(core.bits(16) immediate_in)
    core.bits(16) immediate = immediate_in;
    if core.CurrentCond() != '1110':
        immediate = UNKNOWN = 0;
    if core.GeneralExceptionsToAArch64():
        AArch64.core.CallSupervisor(immediate);
    else:
        core.TakeSVCException(immediate);
# core.HaveFGTExt()
# ============
# Returns True if Fine Grained Trap is implemented, and False otherwise.
boolean core.HaveFGTExt()
    return core.IsFeatureImplemented(FEAT_FGT);
# core.CheckForSVCTrap()
# =========================
# Check for trap on SVC instruction
core.CheckForSVCTrap(core.bits(16) immediate)
    if core.HaveFGTExt():
        route_to_el2 = False;
        if core.APSR.EL == EL0:
            route_to_el2 = (not core.ELUsingAArch32(EL1) and core.EL2Enabled() and HFGITR_EL2.SVC_EL0 == '1' and
                           (HCR_EL2.<E2H, TGE> != '11' and (not core.HaveEL(EL3) or SCR_EL3.FGTEn == '1')));
        if route_to_el2:
            exception = core.ExceptionSyndrome(Exception_SupervisorCall);
            exception.syndrome = core.SetField(exception.syndrome,15,0,immediate);
            exception.trappedsyscallinst = True;
            core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
            vect_offset = 0x0;
            AArch64.core.TakeException(EL2, exception, preferred_exception_return, vect_offset);
# core.EncodeAsyncErrorSyndrome()
# ==================================
# Return the corresponding encoding for ErrorState.
core.bits(2) core.EncodeAsyncErrorSyndrome(ErrorState errorstate)
    case errorstate of
        when ErrorState_UC   return '00';
        when ErrorState_UEU  return '01';
        when ErrorState_UEO  return '10';
        when ErrorState_UER  return '11';
        otherwise core.Unreachable();
# core.ActionRequired()
# ================
# Return an implementation specific value:
# returns True if action is required, False otherwise.
boolean core.ActionRequired();
# core.ErrorIsContained()
# ==================
# Return an implementation specific value:
# True if Error is contained by the PE, False otherwise.
boolean core.ErrorIsContained();
# core.ErrorIsSynchronized()
# =====================
# Return an implementation specific value:
# returns True if Error is synchronized by any synchronization event
# False otherwise.
boolean core.ErrorIsSynchronized();
# core.ReportErrorAsUC()
# =================
# Return an implementation specific value:
# returns True if Error is Uncontainable, False otherwise.
boolean core.ReportErrorAsUC();
# core.ReportErrorAsUER()
# ==================
# Return an implementation specific value:
# returns True if Error is Recoverable, False otherwise.
boolean core.ReportErrorAsUER();
# core.ReportErrorAsUEU()
# ==================
# Return an implementation specific value:
# returns True if Error is Unrecoverable, False otherwise.
boolean core.ReportErrorAsUEU();
# core.StateIsRecoverable()
# =====================
# Return an implementation specific value:
# returns True is PE State is unrecoverable else False.
boolean core.StateIsRecoverable();
# core.PEErrorState()
# ======================
# Returns the error state by PE on taking an SError Interrupt
# to AArch32 level.
ErrorState core.PEErrorState(FaultRecord fault)
    if (not core.ErrorIsContained() or
        (not core.ErrorIsSynchronized() and not core.StateIsRecoverable()) or
         core.ReportErrorAsUC()) then
        return ErrorState_UC;
    if not core.StateIsRecoverable() or core.ReportErrorAsUEU():
        return ErrorState_UEU;
    if core.ActionRequired() or core.ReportErrorAsUER():
        return ErrorState_UER;
    return ErrorState_UEO;
# core.IsAsyncAbort()
# ==============
# Returns True if the abort currently being processed is an asynchronous abort, and False
# otherwise.
boolean core.IsAsyncAbort(Fault statuscode)
    assert statuscode != Fault_None;
    return (statuscode IN {Fault_AsyncExternal, Fault_AsyncParity});
# core.IsAsyncAbort()
# ==============
boolean core.IsAsyncAbort(FaultRecord fault)
    return core.IsAsyncAbort(fault.statuscode);
# core.IsExternalAbort()
# =================
# Returns True if the abort currently being processed is an External abort and False otherwise.
boolean core.IsExternalAbort(Fault statuscode)
    assert statuscode != Fault_None;
    return (statuscode IN {
        Fault_SyncExternal,
        Fault_SyncParity,
        Fault_SyncExternalOnWalk,
        Fault_SyncParityOnWalk,
        Fault_AsyncExternal,
        Fault_AsyncParity
    });
# core.IsExternalAbort()
# =================
boolean core.IsExternalAbort(FaultRecord fault)
    return core.IsExternalAbort(fault.statuscode) or fault.gpcf.gpf == GPCF_EABT;
# core.IsSecondStage()
# ===============
boolean core.IsSecondStage(FaultRecord fault)
    assert fault.statuscode != Fault_None;
    return fault.secondstage;
# core.LSInstructionSyndrome()
# =======================
# Returns the extended syndrome information for a second stage fault.
#  <10>  - Syndrome valid bit. The syndrome is valid only for certain types of access instruction.
#  <9:8> - Access size.
#  <7>   - Sign extended (for loads).
#  <6:2> - Transfer register.
#  <1>   - Transfer register is 64-bit.
#  <0>   - Instruction has acquire/release semantics.
core.bits(11) core.LSInstructionSyndrome();
# core.FaultSyndrome()
# =======================
# Creates an exception syndrome value for Abort and Watchpoint exceptions taken to
# AArch32 Hyp mode.
core.bits(25) core.FaultSyndrome(boolean d_side, FaultRecord fault)
    assert fault.statuscode != Fault_None;
    core.bits(25) iss  = core.Zeros(25);
    core.bits(24) iss2 = core.Zeros(24);
    if core.HaveRASExt() and core.IsAsyncAbort(fault):
        ErrorState errstate = core.PEErrorState(fault);
        iss = core.SetField(iss,11,10,core.EncodeAsyncErrorSyndrome(errstate)); # AET
    if d_side:
        if (core.IsSecondStage(fault) and not fault.s2fs1walk and
            (not core.IsExternalSyncAbort(fault) or
            (not core.HaveRASExt() and fault.access.acctype == AccessType_TTW and
            boolean IMPLEMENTATION_DEFINED "ISV on second stage translation table walk"))) then
            iss = core.SetField(iss,24,14,core.LSInstructionSyndrome());
        if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
            iss = core.SetBit(iss,8,'1')
        if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
            iss = core.SetBit(iss,6,'1')
        elsif fault.statuscode IN {Fault_HWUpdateAccessFlag, Fault_Exclusive}:
            iss = core.SetBit(iss,6,bit UNKNOWN)
        elsif fault.access.atomicop and core.IsExternalAbort(fault):
            iss = core.SetBit(iss,6,bit UNKNOWN)
        else:
            iss = core.SetBit(iss,6,'1' if fault.write else '0')
    if core.IsExternalAbort(fault):
         iss = core.SetBit(iss,9,fault.extflag)
    iss = core.SetBit(iss,7,'1' if fault.s2fs1walk else '0')
    iss = core.SetField(iss,5,0,core.EncodeLDFSC(fault.statuscode, fault.level));
    return (iss);
# core.IPAValid()
# ==========
# Return True if the IPA is reported for the abort
boolean core.IPAValid(FaultRecord fault)
    assert fault.statuscode != Fault_None;
    if fault.gpcf.gpf != GPCF_None:
        return fault.secondstage;
    elsif fault.s2fs1walk:
        return fault.statuscode IN {
            Fault_AccessFlag,
            Fault_Permission,
            Fault_Translation,
            Fault_AddressSize
        };
    elsif fault.secondstage:
        return fault.statuscode IN {
            Fault_AccessFlag,
            Fault_Translation,
            Fault_AddressSize
        };
    else:
        return False;
# core.AbortSyndrome()
# =======================
# Creates an exception syndrome record for Abort  exceptions
# taken to Hyp mode
# from an AArch32 translation regime.
ExceptionRecord core.AbortSyndrome(Exception exceptype, FaultRecord fault,
                                      core.bits(32) vaddress, core.bits(2) target_el)
    exception = core.ExceptionSyndrome(exceptype);
    d_side = exceptype == Exception_DataAbort;
    exception.syndrome = core.FaultSyndrome(d_side, fault);
    exception.vaddress = core.ZeroExtend(vaddress, 64);
    if core.IPAValid(fault):
        exception.ipavalid = True;
        exception.NS = '1' if fault.ipaddress.paspace == PAS_NonSecure else '0';
        exception.ipaddress = core.ZeroExtend(fault.ipaddress.address,  56);
    else:
        exception.ipavalid = False;
    return exception;
# core.EnterMonitorModeInDebugState()
# ======================================
# Take an exception in Debug state to Monitor mode.
core.EnterMonitorModeInDebugState()
    core.SynchronizeContext();
    assert core.HaveEL(EL3) and core.ELUsingAArch32(EL3);
    from_secure = core.CurrentSecurityState() == SS_Secure;
    if core.APSR.M == M32_Monitor:
         SCR.NS = '0';
    core.WriteMode(M32_Monitor);
    SPSR[] = UNKNOWN = 0;
    core.R[14] = UNKNOWN = 0;
    # In Debug state, the PE always execute T32 instructions when in AArch32 state, and
    # core.APSR.{SS,A,I,F} are not observable so behave as UNKNOWN.
    core.APSR.T = '1';                             # core.APSR.J is RES0
    core.APSR.<SS,A,I,F> = UNKNOWN = 0;
    core.APSR.E = SCTLR.EE;
    core.APSR.IL = '0';
    core.APSR.IT = '00000000';
    if core.HavePANExt():
        if not from_secure:
            core.APSR.PAN = '0';
        elsif SCTLR.SPAN == '0':
            core.APSR.PAN = '1';
    if core.HaveSSBSExt():
         core.APSR.SSBS = bit UNKNOWN;
    DLR = UNKNOWN = 0;
    DSPSR = UNKNOWN = 0;
    EDSCR.ERR = '1';
    core.UpdateEDSCRFields();                        # Update EDSCR processor state flags.
    core.EndOfInstruction();
# core.EnterMonitorMode()
# ==========================
# Take an exception to Monitor mode.
core.EnterMonitorMode(core.bits(32) preferred_exception_return, integer lr_offset,
                         integer vect_offset)
    core.SynchronizeContext();
    assert core.HaveEL(EL3) and core.ELUsingAArch32(EL3);
    from_secure = core.CurrentSecurityState() == SS_Secure;
    if core.Halted():
        core.EnterMonitorModeInDebugState();
        return;
    core.bits(32) spsr = core.GetPSRFromcore.APSR(AArch32_NonDebugState, 32);
    if core.APSR.M == M32_Monitor:
         SCR.NS = '0';
    core.WriteMode(M32_Monitor);
    SPSR[] = spsr;
    core.R[14] = preferred_exception_return + lr_offset;
    core.APSR.T = SCTLR.TE;                        # core.APSR.J is RES0
    core.APSR.SS = '0';
    core.APSR.<A,I,F> = '111';
    core.APSR.E = SCTLR.EE;
    core.APSR.IL = '0';
    core.APSR.IT = '00000000';
    if core.HavePANExt():
        if not from_secure:
            core.APSR.PAN = '0';
        elsif SCTLR.SPAN == '0':
            core.APSR.PAN = '1';
    if core.HaveSSBSExt():
         core.APSR.SSBS = SCTLR.DSSBS;
    boolean branch_conditional = False;
    core.BranchTo(core.Field(MVBAR,31,5):core.Field(vect_offset,4,0), 'EXCEPTION', branch_conditional);
    core.CheckExceptionCatch(True);                  # Check for debug event on exception entry
    core.EndOfInstruction();
# core.EncodeSDFSC()
# =============
# Function that gives the Short-descriptor FSR code for different types of Fault
core.bits(5) core.EncodeSDFSC(Fault statuscode, integer level)
    result = 0;
    case statuscode of
        when Fault_AccessFlag
            assert level IN {1,2};
            result = '00011' if level == 1 else '00110';
        when Fault_Alignment
            result = '00001';
        when Fault_Permission
            assert level IN {1,2};
            result = '01101' if level == 1 else '01111';
        when Fault_Domain
            assert level IN {1,2};
            result = '01001' if level == 1 else '01011';
        when Fault_Translation
            assert level IN {1,2};
            result = '00101' if level == 1 else '00111';
        when Fault_SyncExternal
            result = '01000';
        when Fault_SyncExternalOnWalk
            assert level IN {1,2};
            result = '01100' if level == 1 else '01110';
        when Fault_SyncParity
            result = '11001';
        when Fault_SyncParityOnWalk
            assert level IN {1,2};
            result = '11100' if level == 1 else '11110';
        when Fault_AsyncParity
            result = '11000';
        when Fault_AsyncExternal
            result = '10110';
        when Fault_Debug
            result = '00010';
        when Fault_TLBConflict
            result = '10000';
        when Fault_Lockdown
            result = '10100';   # IMPLEMENTATION DEFINED
        when Fault_Exclusive
            result = '10101';   # IMPLEMENTATION DEFINED
        when Fault_ICacheMaint
            result = '00100';
        otherwise
            core.Unreachable();
    return result;
# core.CommonFaultStatus()
# ===========================
# Return the common part of the fault status on reporting a Data
# or Prefetch Abort.
core.bits(32) core.CommonFaultStatus(FaultRecord fault, boolean long_format)
    core.bits(32) target = core.Zeros(32);
    if core.HaveRASExt() and core.IsAsyncAbort(fault):
        ErrorState errstate = core.PEErrorState(fault);
        target = core.SetField(target,15,14,core.EncodeAsyncErrorSyndrome(errstate));   # AET
    if core.IsExternalAbort(fault):
         target = core.SetBit(target,12,fault.extflag)        # ExT
    target = core.SetBit(target,9,'1' if long_format else '0')                     # LPAE
    if long_format:
                                                       # Long-descriptor format
        target = core.SetField(target,5,0,core.EncodeLDFSC(fault.statuscode, fault.level));  # STATUS
    else                                                              # Short-descriptor format
        target<10,3:0> = core.EncodeSDFSC(fault.statuscode, fault.level);  # FS
    return target;
# core.ReportDataAbort()
# =========================
# Report syndrome information for aborts taken to modes other than Hyp mode.
core.ReportDataAbort(boolean route_to_monitor, FaultRecord fault,
                        core.bits(32) vaddress)
    long_format = False;
    if route_to_monitor and core.CurrentSecurityState() != SS_Secure:
        long_format = ((TTBCR_S.EAE == '1') or
                       (core.IsExternalSyncAbort(fault) and ((core.APSR.EL == EL2 or TTBCR.EAE == '1') or
                        (fault.secondstage and (boolean IMPLEMENTATION_DEFINED
                                               "Report abort using Long-descriptor format")))));
    else:
        long_format = TTBCR.EAE == '1';
    core.bits(32) syndrome = core.CommonFaultStatus(fault, long_format);
    # bits of syndrome that are not common to I and D side
    if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
        syndrome = core.SetBit(syndrome,13,'1')                              # CM
        syndrome = core.SetBit(syndrome,11,'1')                              # WnR
    else:
        syndrome = core.SetBit(syndrome,11,'1' if fault.write else '0') # WnR
    if not long_format:
        syndrome = core.SetField(syndrome,7,4,fault.domain);                    # Domain
    if fault.access.acctype == AccessType_IC:
        i_syndrome = 0;
        if (not long_format and
            boolean IMPLEMENTATION_DEFINED "Report I-cache maintenance fault in IFSR") then
            i_syndrome = syndrome;
            syndrome<10,3:0> = core.EncodeSDFSC(Fault_ICacheMaint, 1);
        else:
            i_syndrome = UNKNOWN = 0;
        if route_to_monitor:
            IFSR_S = i_syndrome;
        else:
            IFSR = i_syndrome;
    if route_to_monitor:
        DFSR_S = syndrome;
        DFAR_S = vaddress;
    else:
        DFSR = syndrome;
        DFAR = vaddress;
    return;
# core.EffectiveEA()
# =============
# Returns effective SCR_EL3.EA value
bit core.EffectiveEA()
    if core.Halted() and EDSCR.SDD == '0':
        return '0';
    else:
        return SCR_EL3.EA if core.HaveAArch64() else SCR.EA;
# core.IsDebugException()
# ==================
boolean core.IsDebugException(FaultRecord fault)
    assert fault.statuscode != Fault_None;
    return fault.statuscode == Fault_Debug;
# core.TakeDataAbortException()
# ================================
core.TakeDataAbortException(core.bits(32) vaddress, FaultRecord fault)
    route_to_monitor = core.HaveEL(EL3) and core.EffectiveEA() == '1' and core.IsExternalAbort(fault);
    route_to_hyp = (core.EL2Enabled() and core.APSR.EL IN {EL0, EL1} and
                    (HCR.TGE == '1' or
                     (core.HaveRASExt() and HCR2.TEA == '1' and core.IsExternalAbort(fault)) or
                     (core.IsDebugException(fault) and HDCR.TDE == '1') or
                     core.IsSecondStage(fault)));
    core.bits(32) preferred_exception_return = core.ThisInstrAddr(32);
    vect_offset = 0x10;
    lr_offset = 8;
    if core.IsDebugException(fault):
         DBGDSCRext.MOE = fault.debugmoe;
    if route_to_monitor:
        core.ReportDataAbort(route_to_monitor, fault, vaddress);
        core.EnterMonitorMode(preferred_exception_return, lr_offset, vect_offset);
    elsif core.APSR.EL == EL2 or route_to_hyp:
        exception = core.AbortSyndrome(Exception_DataAbort, fault, vaddress, EL2);
        if core.APSR.EL == EL2:
            core.EnterHypMode(exception, preferred_exception_return, vect_offset);
        else:
            core.EnterHypMode(exception, preferred_exception_return, 0x14);
    else:
        core.ReportDataAbort(route_to_monitor, fault, vaddress);
        core.EnterMode(M32_Abort, preferred_exception_return, lr_offset, vect_offset);
# core.ReportPrefetchAbort()
# =============================
# Report syndrome information for aborts taken to modes other than Hyp mode.
core.ReportPrefetchAbort(boolean route_to_monitor, FaultRecord fault, core.bits(32) vaddress)
    # The encoding used in the IFSR can be Long-descriptor format or Short-descriptor format.
    # Normally, the current translation table format determines the format. For an abort from
    # Non-secure state to Monitor mode, the IFSR uses the Long-descriptor format if any of the
    # following applies:
    # * The Secure TTBCR.EAE is set to 1.
    # * It is taken from Hyp mode.
    # * It is taken from EL1 or EL0, and the Non-secure TTBCR.EAE is set to 1.
    long_format = False;
    if route_to_monitor and core.CurrentSecurityState() != SS_Secure:
        long_format = TTBCR_S.EAE == '1' or core.APSR.EL == EL2 or TTBCR.EAE == '1';
    else:
        long_format = TTBCR.EAE == '1';
    core.bits(32) fsr = core.CommonFaultStatus(fault, long_format);
    if route_to_monitor:
        IFSR_S = fsr;
        IFAR_S = vaddress;
    else:
        IFSR = fsr;
        IFAR = vaddress;
    return;
# core.TakePrefetchAbortException()
# ====================================
core.TakePrefetchAbortException(core.bits(32) vaddress, FaultRecord fault)
    route_to_monitor = core.HaveEL(EL3) and core.EffectiveEA() == '1' and core.IsExternalAbort(fault);
    route_to_hyp = (core.EL2Enabled() and core.APSR.EL IN {EL0, EL1} and
                    (HCR.TGE == '1' or
                     (core.HaveRASExt() and HCR2.TEA == '1' and core.IsExternalAbort(fault)) or
                     (core.IsDebugException(fault) and HDCR.TDE == '1') or
                     core.IsSecondStage(fault)));
    ExceptionRecord exception;
    core.bits(32) preferred_exception_return = core.ThisInstrAddr(32);
    vect_offset = 0x0C;
    lr_offset = 4;
    if core.IsDebugException(fault):
         DBGDSCRext.MOE = fault.debugmoe;
    if route_to_monitor:
        core.ReportPrefetchAbort(route_to_monitor, fault, vaddress);
        core.EnterMonitorMode(preferred_exception_return, lr_offset, vect_offset);
    elsif core.APSR.EL == EL2 or route_to_hyp:
        if fault.statuscode == Fault_Alignment:             # PC Alignment fault
            exception = core.ExceptionSyndrome(Exception_PCAlignment);
            exception.vaddress = core.ThisInstrAddr(64);
        else:
            exception = core.AbortSyndrome(Exception_InstructionAbort, fault, vaddress, EL2);
        if core.APSR.EL == EL2:
            core.EnterHypMode(exception, preferred_exception_return, vect_offset);
        else:
            core.EnterHypMode(exception, preferred_exception_return, 0x14);
    else:
        core.ReportPrefetchAbort(route_to_monitor, fault, vaddress);
        core.EnterMode(M32_Abort, preferred_exception_return, lr_offset, vect_offset);
# AArch64.core.EncodeSyncErrorSyndrome()
# =================================
# Return the encoding for corresponding ErrorState.
core.bits(2) AArch64.core.EncodeSyncErrorSyndrome(ErrorState errorstate)
    case errorstate of
        when ErrorState_UC  return '10';
        when ErrorState_UEO return '11';
        when ErrorState_UER return '00';
        otherwise core.Unreachable();
# core.ExtAbortToA64()
# ===============
# Returns True if synchronous exception is being taken to A64 exception
# level.
boolean core.ExtAbortToA64(FaultRecord fault)
    # Check if routed to AArch64 state
    route_to_aarch64 = core.APSR.EL == EL0 and not core.ELUsingAArch32(EL1);
    if not route_to_aarch64 and core.EL2Enabled() and not core.ELUsingAArch32(EL2):
        route_to_aarch64 = (HCR_EL2.TGE == '1' or core.IsSecondStage(fault) or
                            (core.HaveRASExt() and HCR_EL2.TEA == '1' and core.IsExternalAbort(fault)) or
                            (core.IsDebugException(fault) and MDCR_EL2.TDE == '1'));
    if not route_to_aarch64 and core.HaveEL(EL3) and not core.ELUsingAArch32(EL3):
        route_to_aarch64 = SCR_GEN[].EA == '1' and core.IsExternalAbort(fault);
    return route_to_aarch64 and core.IsExternalSyncAbort(fault.statuscode);
# core.FaultIsCorrected()
# ==================
# Return an implementation specific value:
# True if fault is corrected by the PE, False otherwise.
boolean core.FaultIsCorrected();
# core.ReportErrorAsIMPDEF()
# =====================
# Return an implementation specific value:
# returns True if Error is IMPDEF, False otherwise.
boolean core.ReportErrorAsIMPDEF();
# core.ReportErrorAsUncategorized()
# ===========================
# Return an implementation specific value:
# returns True if Error is uncategorized, False otherwise.
boolean core.ReportErrorAsUncategorized();
# AArch64.core.PEErrorState()
# ======================
# Returns the error state by PE on taking a Synchronous
# or Asynchronous exception.
ErrorState AArch64.core.PEErrorState(FaultRecord fault)
    if not core.IsExternalSyncAbort(fault) and core.ExtAbortToA64(fault):
        if core.ReportErrorAsUncategorized():
            return ErrorState_Uncategorized;
        if core.ReportErrorAsIMPDEF():
            return ErrorState_IMPDEF;
    assert not core.FaultIsCorrected();
    if (not core.ErrorIsContained() or
        (not core.ErrorIsSynchronized() and not core.StateIsRecoverable()) or
         core.ReportErrorAsUC()) then
        return ErrorState_UC;
    if not core.StateIsRecoverable() or core.ReportErrorAsUEU():
        if core.IsExternalSyncAbort(fault):  # Implies taken to AArch64
            return ErrorState_UC;
        else:
            return ErrorState_UEU;
    if (core.ActionRequired() or core.ReportErrorAsUER()):
        return ErrorState_UER;
    return ErrorState_UEO;
# core.GetLoadStoreType()
# ==================
# Returns the Load/Store Type. Used when a Translation fault,
# Access flag fault, or Permission fault generates a Data Abort.
core.bits(2) core.GetLoadStoreType();
# core.HaveFeatLS64()
# ==============
# Returns True if the LD64B, ST64B instructions are
# supported, and False otherwise.
boolean core.HaveFeatLS64()
    return core.IsFeatureImplemented(FEAT_LS64);
# core.LS64InstructionSyndrome()
# =========================
# Returns the syndrome information and LST for a Data Abort by a
# ST64B, ST64BV, ST64BV0, or LD64B instruction. The syndrome information
# includes the ISS2, extended syndrome field.
(core.bits(24), core.bits(11)) core.LS64InstructionSyndrome();
# AArch64.core.FaultSyndrome()
# =======================
# Creates an exception syndrome value for Abort and Watchpoint exceptions taken to
# an Exception level using AArch64.
(core.bits(25), core.bits(24)) AArch64.core.FaultSyndrome(boolean d_side, FaultRecord fault, boolean pavalid)
    assert fault.statuscode != Fault_None;
    core.bits(25) iss  = core.Zeros(25);
    core.bits(24) iss2 = core.Zeros(24);
    if core.HaveRASExt() and fault.statuscode == Fault_SyncExternal:
        ErrorState errstate = AArch64.core.PEErrorState(fault);
        iss = core.SetField(iss,12,11,AArch64.core.EncodeSyncErrorSyndrome(errstate));  # SET
    if d_side:
        if fault.access.acctype == AccessType_GCS:
            iss2 = core.SetBit(iss2,8,'1')
        if core.HaveFeatLS64() and fault.access.ls64:
            if (fault.statuscode IN {Fault_AccessFlag, Fault_Translation, Fault_Permission}):
                (iss2, core.Field(iss,24,14)) = core.LS64InstructionSyndrome();
        elsif (core.IsSecondStage(fault) and not fault.s2fs1walk and
               (not core.IsExternalSyncAbort(fault) or
               (not core.HaveRASExt() and fault.access.acctype == AccessType_TTW and
               boolean IMPLEMENTATION_DEFINED "ISV on second stage translation table walk"))) then
            iss = core.SetField(iss,24,14,core.LSInstructionSyndrome());
        if core.HaveNV2Ext() and fault.access.acctype == AccessType_NV2:
            iss = core.SetBit(iss,13,'1')   # Fault is generated by use of VNCR_EL2
        if core.HaveFeatLS64() and fault.statuscode IN {Fault_AccessFlag, Fault_Translation,
                                                  Fault_Permission} then
            iss = core.SetField(iss,12,11,core.GetLoadStoreType());
        if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
            iss = core.SetBit(iss,8,'1')
        if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
            iss = core.SetBit(iss,6,'1')
        elsif fault.statuscode IN {Fault_HWUpdateAccessFlag, Fault_Exclusive}:
            iss = core.SetBit(iss,6,bit UNKNOWN)
        elsif fault.access.atomicop and core.IsExternalAbort(fault):
            iss = core.SetBit(iss,6,bit UNKNOWN)
        else:
            iss = core.SetBit(iss,6,'1' if fault.write else '0')
        if fault.statuscode == Fault_Permission:
            iss2 = core.SetBit(iss2,5,'1' if fault.dirtybit else '0')
            iss2 = core.SetBit(iss2,6,'1' if fault.overlay else '0')
            if core.Bit(iss,24) == '0':
                iss = core.SetBit(iss,21,'1' if fault.toplevel else '0')
            iss2 = core.SetBit(iss2,7,'1' if fault.assuredonly else '0')
            iss2 = core.SetBit(iss2,9,'1' if fault.tagaccess else '0')
            iss2 = core.SetBit(iss2,10,'1' if fault.s1tagnotdata else '0')
    else:
        if fault.access.acctype == AccessType_IFETCH and fault.statuscode == Fault_Permission:
            iss = core.SetBit(iss,21,'1' if fault.toplevel else '0')
            iss2 = core.SetBit(iss2,7,'1' if fault.assuredonly else '0')
            iss2 = core.SetBit(iss2,6,'1' if fault.overlay else '0')
    if core.IsExternalAbort(fault):
         iss = core.SetBit(iss,9,fault.extflag)
    iss = core.SetBit(iss,7,'1' if fault.s2fs1walk else '0')
    iss = core.SetField(iss,5,0,core.EncodeLDFSC(fault.statuscode, fault.level));
    return (iss, iss2);
# core.HaveMTE4Ext()
# =============
# Returns True if functionality in FEAT_MTE4 is implemented, and False otherwise.
boolean core.HaveMTE4Ext()
    return core.IsFeatureImplemented(FEAT_MTE4);
# core.HavePFAR()
# ==========
# Returns True if the Physical Fault Address Extension is implemented, and False
# otherwise.
boolean core.HavePFAR()
    return core.IsFeatureImplemented(FEAT_PFAR);
# AArch64.core.AbortSyndrome()
# =======================
# Creates an exception syndrome record for Abort and Watchpoint exceptions
#
# from an AArch64 translation regime.
ExceptionRecord AArch64.core.AbortSyndrome(Exception exceptype, FaultRecord fault,
                                      core.bits(64) vaddress, core.bits(2) target_el)
    exception = core.ExceptionSyndrome(exceptype);
    d_side = exceptype IN {Exception_DataAbort, Exception_NV2DataAbort, Exception_Watchpoint,
                           Exception_NV2Watchpoint};
    if (core.HavePFAR() and
            ((core.EL2Enabled() and HCR_EL2.VM == '1' and target_el == EL1) or
             not core.IsExternalSyncAbort(fault))) then
        exception.pavalid = False;
    else:
        exception.pavalid = boolean IMPLEMENTATION_DEFINED "PFAR_ELx is valid";
    (exception.syndrome, exception.syndrome2) = AArch64.core.FaultSyndrome(d_side, fault,
                                                                      exception.pavalid);
    if fault.statuscode == Fault_TagCheck:
        if core.HaveMTE4Ext():
            exception.vaddress = core.ZeroExtend(vaddress, 64);
        else:
            exception.vaddress = core.bits(4) UNKNOWN : core.Field(vaddress,59,0);
    else:
        exception.vaddress = core.ZeroExtend(vaddress, 64);
    if core.IPAValid(fault):
        exception.ipavalid = True;
        exception.NS = '1' if fault.ipaddress.paspace == PAS_NonSecure else '0';
        exception.ipaddress = fault.ipaddress.address;
    else:
        exception.ipavalid = False;
    return exception;
# AArch64.core.BreakpointException()
# =============================
AArch64.core.BreakpointException(FaultRecord fault)
    assert core.APSR.EL != EL3;
    route_to_el2 = (core.APSR.EL IN {EL0, EL1} and core.EL2Enabled() and
                    (HCR_EL2.TGE == '1' or MDCR_EL2.TDE == '1'));
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    target_el = 0;
    vect_offset = 0x0;
    target_el = EL2 if (core.APSR.EL == EL2 or route_to_el2) else EL1;
    vaddress = UNKNOWN = 0;
    exception = AArch64.core.AbortSyndrome(Exception_Breakpoint, fault, vaddress, target_el);
    AArch64.core.TakeException(target_el, exception, preferred_exception_return, vect_offset);
# core.HaveDoubleFault2Ext()
# =====================
# Returns True if support for the DoubleFault2 feature is implemented, and False otherwise.
boolean core.HaveDoubleFault2Ext()
    return core.IsFeatureImplemented(FEAT_DoubleFault2);
# core.HaveFeatSCTLR2()
# ================
# Returns True if SCTLR2 extension
# support is implemented and False otherwise.
boolean core.HaveFeatSCTLR2()
    return core.IsFeatureImplemented(FEAT_SCTLR2);
# core.HaveFeatHCX()
# =============
# Returns True if HCRX_EL2 Trap Control register is implemented,
# and False otherwise.
boolean core.HaveFeatHCX()
    return core.IsFeatureImplemented(FEAT_HCX);
# core.IsHCRXEL2Enabled()
# ==================
# Returns True if access to HCRX_EL2 register is enabled, and False otherwise.
# Indirect read of HCRX_EL2 returns 0 when access is not enabled.
boolean core.IsHCRXEL2Enabled()
    if not core.HaveFeatHCX():
         return False;
    if core.HaveEL(EL3) and SCR_EL3.HXEn == '0':
        return False;
    return core.EL2Enabled();
# core.IsSCTLR2EL1Enabled()
# ====================
# Returns True if access to SCTLR2_EL1 register is enabled, and False otherwise.
# Indirect read of SCTLR2_EL1 returns 0 when access is not enabled.
boolean core.IsSCTLR2EL1Enabled()
    if not core.HaveFeatSCTLR2():
         return False;
    if core.HaveEL(EL3) and SCR_EL3.SCTLR2En == '0':
        return False;
    elsif (core.EL2Enabled() and (not core.IsHCRXEL2Enabled() or HCRX_EL2.SCTLR2En == '0')):
        return False;
    else:
        return True;
# core.IsSCTLR2EL2Enabled()
# ====================
# Returns True if access to SCTLR2_EL2 register is enabled, and False otherwise.
# Indirect read of SCTLR2_EL2 returns 0 when access is not enabled.
boolean core.IsSCTLR2EL2Enabled()
    if not core.HaveFeatSCTLR2():
         return False;
    if core.HaveEL(EL3) and SCR_EL3.SCTLR2En == '0':
        return False;
    return core.EL2Enabled();
# AArch64.core.RouteToSErrorOffset()
# =============================
# Returns True if synchronous External abort exceptions are taken to the
# appropriate SError vector offset, and False otherwise.
boolean AArch64.core.RouteToSErrorOffset(core.bits(2) target_el)
    if not core.HaveDoubleFaultExt():
         return False;
    bit ease_bit;
    case target_el of
        when EL3
            ease_bit = SCR_EL3.EASE;
        when EL2
            if core.HaveDoubleFault2Ext() and core.IsSCTLR2EL2Enabled():
                ease_bit = SCTLR2_EL2.EASE;
            else:
                ease_bit = '0';
        when EL1
            if core.HaveDoubleFault2Ext() and core.IsSCTLR2EL1Enabled():
                ease_bit = SCTLR2_EL1.EASE;
            else:
                ease_bit = '0';
    return (ease_bit == '1');
# AArch64.core.SyncExternalAbortTarget()
# =================================
# Returns the target Exception level for a Synchronous External
# Data or Instruction Abort.
core.bits(2) AArch64.core.SyncExternalAbortTarget(FaultRecord fault)
    route_to_el3 = False;
    # The exception is explicitly routed to EL3
    if core.APSR.EL != EL3:
        route_to_el3 = (core.HaveEL(EL3) and core.EffectiveEA() == '1');
    else:
        route_to_el3 = False;
    # The exception is explicitly routed to EL2
    bit tea_bit = (HCR_EL2.TEA if core.HaveRASExt() else '0');
    route_to_el2 = False;
    if not route_to_el3 and core.EL2Enabled() and core.APSR.EL == EL1:
        route_to_el2 = (tea_bit == '1' or
                        fault.access.acctype == AccessType_NV2 or
                        core.IsSecondStage(fault));
    elsif not route_to_el3 and core.EL2Enabled() and core.APSR.EL == EL0:
        route_to_el2 = (not core.IsInHost() and (HCR_EL2.TGE == '1' or tea_bit == '1' or
                        core.IsSecondStage(fault)));
    else:
        route_to_el2 = False;
    route_masked_to_el3 = False;
    route_masked_to_el2 = False;
    if core.HaveDoubleFault2Ext():
        # The masked exception is routed to EL2
        route_masked_to_el2 = (core.EL2Enabled() and not route_to_el3 and
                               (core.APSR.EL == EL1 and core.APSR.A == '1') and
                               core.IsHCRXEL2Enabled() and HCRX_EL2.TMEA == '1');
        # The masked exception is routed to EL3
        route_masked_to_el3 = (core.HaveEL(EL3) and
                               not (route_to_el2 or route_masked_to_el2) and
                               (core.APSR.EL IN {EL2, EL1} and core.APSR.A == '1') and
                               SCR_EL3.TMEA == '1');
    else:
        route_masked_to_el2 = False;
        route_masked_to_el3 = False;
    # The exception is taken at EL3
    take_in_el3 = core.APSR.EL == EL3;
    # The exception is taken at EL2 or in the Host EL0
    take_in_el2_0 = ((core.APSR.EL == EL2 or core.IsInHost()) and
                     not (route_to_el3 or route_masked_to_el3));
    # The exception is taken at EL1 or in the non-Host EL0
    take_in_el1_0 = ((core.APSR.EL == EL1 or (core.APSR.EL == EL0 and not core.IsInHost())) and
                     not (route_to_el2 or route_masked_to_el2) and
                     not (route_to_el3 or route_masked_to_el3));
    target_el = 0;
    if take_in_el3 or route_to_el3 or route_masked_to_el3:
        target_el = EL3;
    elsif take_in_el2_0 or route_to_el2 or route_masked_to_el2:
        target_el = EL2;
    elsif take_in_el1_0:
        target_el = EL1;
    else:
        core.assert(False);
    return target_el;
# AArch64.core.DataAbort()
# ===================
AArch64.core.DataAbort(core.bits(64) vaddress, FaultRecord fault)
    target_el = 0;
    if core.IsExternalAbort(fault):
        target_el = AArch64.core.SyncExternalAbortTarget(fault);
    else:
        route_to_el2 = (core.EL2Enabled() and core.APSR.EL IN {EL0, EL1} and
                        (HCR_EL2.TGE == '1' or
                         (core.HaveRME() and fault.gpcf.gpf == GPCF_Fail and HCR_EL2.GPF == '1') or
                         (core.HaveNV2Ext() and fault.access.acctype == AccessType_NV2) or
                         core.IsSecondStage(fault)));
        if core.APSR.EL == EL3:
            target_el = EL3;
        elsif core.APSR.EL == EL2 or route_to_el2:
            target_el = EL2;
        else:
            target_el = EL1;
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    vect_offset = 0;
    if core.IsExternalAbort(fault) and AArch64.core.RouteToSErrorOffset(target_el):
        vect_offset = 0x180;
    else:
        vect_offset = 0x0;
    ExceptionRecord exception;
    if core.HaveNV2Ext() and fault.access.acctype == AccessType_NV2:
        exception = AArch64.core.AbortSyndrome(Exception_NV2DataAbort, fault, vaddress, target_el);
    else:
        exception = AArch64.core.AbortSyndrome(Exception_DataAbort, fault, vaddress, target_el);
    AArch64.core.TakeException(target_el, exception, preferred_exception_return, vect_offset);
# AArch64.core.InstructionAbort()
# ==========================
AArch64.core.InstructionAbort(core.bits(64) vaddress, FaultRecord fault)
    # External aborts on instruction fetch must be taken synchronously
    if core.HaveDoubleFaultExt():
         assert fault.statuscode != Fault_AsyncExternal;
    target_el = 0;
    if core.IsExternalAbort(fault):
        target_el = AArch64.core.SyncExternalAbortTarget(fault);
    else:
        route_to_el2 = (core.EL2Enabled() and core.APSR.EL IN {EL0, EL1} and
                        (HCR_EL2.TGE == '1' or
                         (core.HaveRME() and fault.gpcf.gpf == GPCF_Fail and HCR_EL2.GPF == '1') or
                         core.IsSecondStage(fault)));
        if core.APSR.EL == EL3:
            target_el = EL3;
        elsif core.APSR.EL == EL2 or route_to_el2:
            target_el = EL2;
        else:
            target_el = EL1;
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    vect_offset = 0;
    if core.IsExternalAbort(fault) and AArch64.core.RouteToSErrorOffset(target_el):
        vect_offset = 0x180;
    else:
        vect_offset = 0x0;
    ExceptionRecord exception = AArch64.core.AbortSyndrome(Exception_InstructionAbort, fault,
                                                      vaddress, target_el);
    AArch64.core.TakeException(target_el, exception, preferred_exception_return, vect_offset);
# AArch64.core.VectorCatchException()
# ==============================
# Vector Catch taken from EL0 or EL1 to EL2. This can only be called when debug exceptions are
# being routed to EL2, as Vector Catch is a legacy debug event.
AArch64.core.VectorCatchException(FaultRecord fault)
    assert core.APSR.EL != EL2;
    assert core.EL2Enabled() and (HCR_EL2.TGE == '1' or MDCR_EL2.TDE == '1');
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    vect_offset = 0x0;
    vaddress = UNKNOWN = 0;
    exception = AArch64.core.AbortSyndrome(Exception_VectorCatch, fault, vaddress, EL2);
    AArch64.core.TakeException(EL2, exception, preferred_exception_return, vect_offset);
# AArch64.core.WatchpointException()
# =============================
AArch64.core.WatchpointException(core.bits(64) vaddress, FaultRecord fault)
    assert core.APSR.EL != EL3;
    route_to_el2 = (core.APSR.EL IN {EL0, EL1} and core.EL2Enabled() and
                    (HCR_EL2.TGE == '1' or MDCR_EL2.TDE == '1'));
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    target_el = 0;
    vect_offset = 0x0;
    target_el = EL2 if (core.APSR.EL == EL2 or route_to_el2) else EL1;
    ExceptionRecord exception;
    if core.HaveNV2Ext() and fault.access.acctype == AccessType_NV2:
        exception = AArch64.core.AbortSyndrome(Exception_NV2Watchpoint, fault, vaddress, target_el);
    else:
        exception = AArch64.core.AbortSyndrome(Exception_Watchpoint, fault, vaddress, target_el);
    AArch64.core.TakeException(target_el, exception, preferred_exception_return, vect_offset);
constant core.bits(4) DebugException_Breakpoint  = '0001';
constant core.bits(4) DebugException_BKPT        = '0011';
constant core.bits(4) DebugException_VectorCatch = '0101';
constant core.bits(4) DebugException_Watchpoint  = '1010';
# core.ReportAsGPCException()
# ======================
# Determine whether the given GPCF is reported as a Granule Protection Check Exception
# rather than a Data or Instruction Abort
boolean core.ReportAsGPCException(FaultRecord fault)
    assert core.HaveRME();
    assert fault.statuscode IN {Fault_GPCFOnWalk, Fault_GPCFOnOutput};
    assert fault.gpcf.gpf != GPCF_None;
    case fault.gpcf.gpf of
        when GPCF_Walk        return True;
        when GPCF_AddressSize return True;
        when GPCF_EABT        return True;
        when GPCF_Fail        return SCR_EL3.GPF == '1' and core.APSR.EL != EL3;
# core.EncodeGPCSC()
# =============
# Function that gives the GPCSC code for types of GPT Fault
core.bits(6) core.EncodeGPCSC(GPCFRecord gpcf)
    assert gpcf.level IN {0,1};
    case gpcf.gpf of
        when GPCF_AddressSize return '00000':core.Bit(gpcf.level,0);
        when GPCF_Walk        return '00010':core.Bit(gpcf.level,0);
        when GPCF_Fail        return '00110':core.Bit(gpcf.level,0);
        when GPCF_EABT        return '01010':core.Bit(gpcf.level,0);
# core.HaveAccessFlagUpdateExt()
# =========================
boolean core.HaveAccessFlagUpdateExt()
    return core.IsFeatureImplemented(FEAT_HAFDBS);
# core.HaveAtomicExt()
# ===============
boolean core.HaveAtomicExt()
    return core.IsFeatureImplemented(FEAT_LSE);
# core.HaveDirtyBitModifierExt()
# =========================
boolean core.HaveDirtyBitModifierExt()
    return core.IsFeatureImplemented(FEAT_HAFDBS);
# core.TakeGPCException()
# ==================
# Report Granule Protection Exception faults
core.TakeGPCException(core.bits(64) vaddress, FaultRecord fault)
    assert core.HaveRME();
    assert core.HaveAtomicExt();
    assert core.HaveAccessFlagUpdateExt();
    assert core.HaveDirtyBitModifierExt();
    assert core.HaveDoubleFaultExt();
    ExceptionRecord exception;
    exception.exceptype = Exception_GPC;
    exception.vaddress  = core.ZeroExtend(vaddress, 64);
    exception.paddress  = fault.paddress;
    exception.pavalid   = True;
    if core.IPAValid(fault):
        exception.ipavalid  = True;
        exception.NS        = '1' if fault.ipaddress.paspace == PAS_NonSecure else '0';
        exception.ipaddress = fault.ipaddress.address;
    else:
        exception.ipavalid = False;
    if fault.access.acctype == AccessType_GCS:
        exception.syndrome2 = core.SetBit(exception.syndrome2,8,'1') #GCS
    # Populate the fields grouped in ISS
    exception.syndrome = core.SetField(exception.syndrome,24,22,core.Zeros(3)); # RES0
    exception.syndrome = core.SetBit(exception.syndrome,21,'1' if fault.gpcfs2walk else '0')  # S2PTW
    if fault.access.acctype == AccessType_IFETCH:
        exception.syndrome = core.SetBit(exception.syndrome,20,'1') # InD
    else:
        exception.syndrome = core.SetBit(exception.syndrome,20,'0') # InD
    exception.syndrome = core.SetField(exception.syndrome,19,14,core.EncodeGPCSC(fault.gpcf)); # GPCSC
    if core.HaveNV2Ext() and fault.access.acctype == AccessType_NV2:
        exception.syndrome = core.SetBit(exception.syndrome,13,'1') # VNCR
    else:
        exception.syndrome = core.SetBit(exception.syndrome,13,'0') # VNCR
    exception.syndrome = core.SetField(exception.syndrome,12,11,'00'); # RES0
    exception.syndrome = core.SetField(exception.syndrome,10,9,'00'); # RES0
    if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
        exception.syndrome = core.SetBit(exception.syndrome,8,'1') # CM
    else:
        exception.syndrome = core.SetBit(exception.syndrome,8,'0')  # CM
    exception.syndrome = core.SetBit(exception.syndrome,7,'1' if fault.s2fs1walk else '0') # S1PTW
    if fault.access.acctype IN {AccessType_DC, AccessType_IC, AccessType_AT}:
        exception.syndrome = core.SetBit(exception.syndrome,6,'1')                              # WnR
    elsif fault.statuscode IN {Fault_HWUpdateAccessFlag, Fault_Exclusive}:
        exception.syndrome = core.SetBit(exception.syndrome,6,bit UNKNOWN)                      # WnR
    elsif fault.access.atomicop and core.IsExternalAbort(fault):
        exception.syndrome = core.SetBit(exception.syndrome,6,bit UNKNOWN)                      # WnR
    else:
        exception.syndrome = core.SetBit(exception.syndrome,6,'1' if fault.write else '0') # WnR
    exception.syndrome = core.SetField(exception.syndrome,5,0,core.EncodeLDFSC(fault.statuscode, fault.level)); # xFSC
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    core.bits(2) target_el = EL3;
    vect_offset = 0;
    if core.IsExternalAbort(fault) and AArch64.core.RouteToSErrorOffset(target_el):
        vect_offset = 0x180;
    else:
        vect_offset = 0x0;
    AArch64.core.TakeException(target_el, exception, preferred_exception_return, vect_offset);
# AArch64.core.Abort()
# ===============
# Abort and Debug exception handling in an AArch64 translation regime.
AArch64.core.Abort(core.bits(64) vaddress, FaultRecord fault)
    if core.IsDebugException(fault):
        if fault.access.acctype == AccessType_IFETCH:
            if core.UsingAArch32() and fault.debugmoe == DebugException_VectorCatch:
                AArch64.core.VectorCatchException(fault);
            else:
                AArch64.core.BreakpointException(fault);
        else:
            AArch64.core.WatchpointException(vaddress, fault);
    elsif fault.gpcf.gpf != GPCF_None and core.ReportAsGPCException(fault):
        core.TakeGPCException(vaddress, fault);
    elsif fault.access.acctype == AccessType_IFETCH:
        AArch64.core.InstructionAbort(vaddress, fault);
    else:
        AArch64.core.DataAbort(vaddress, fault);
# core.Abort()
# ===============
# Abort and Debug exception handling in an AArch32 translation regime.
core.Abort(core.bits(32) vaddress, FaultRecord fault)
    # Check if routed to AArch64 state
    route_to_aarch64 = core.APSR.EL == EL0 and not core.ELUsingAArch32(EL1);
    if not route_to_aarch64 and core.EL2Enabled() and not core.ELUsingAArch32(EL2):
        route_to_aarch64 = (HCR_EL2.TGE == '1' or core.IsSecondStage(fault) or
                            (core.HaveRASExt() and HCR_EL2.TEA == '1' and core.IsExternalAbort(fault)) or
                            (core.IsDebugException(fault) and MDCR_EL2.TDE == '1'));
    if not route_to_aarch64 and core.HaveEL(EL3) and not core.ELUsingAArch32(EL3):
        route_to_aarch64 = core.EffectiveEA() == '1' and core.IsExternalAbort(fault);
    if route_to_aarch64:
        AArch64.core.Abort(core.ZeroExtend(vaddress,  64), fault);
    elsif fault.access.acctype == AccessType_IFETCH:
        core.TakePrefetchAbortException(vaddress, fault);
    else:
        core.TakeDataAbortException(vaddress, fault);
# core.BreakpointValueMatch()
# ==============================
# The first result is whether an Address Match or Context breakpoint is programmed on the
# instruction at "address". The second result is whether an Address Mismatch breakpoint is
# programmed on the instruction, that is, whether the instruction should be stepped.
(boolean, boolean) core.BreakpointValueMatch(integer n_in, core.bits(32) vaddress, boolean linked_to)
    # "n" is the identity of the breakpoint unit to match against.
    # "vaddress" is the current instruction address, ignored if linked_to is True and for Context
    #   matching breakpoints.
    # "linked_to" is True if this is a call from StateMatch for linking.
    integer n = n_in;
    # If a non-existent breakpoint then it is CONSTRAINED raise Exception('UNPREDICTABLE') whether this gives
    # no match or the breakpoint is mapped to another UNKNOWN implemented breakpoint.
    if n >= core.NumBreakpointsImplemented():
        Constraint c;
        (c, n) = core.ConstrainUnpredictableInteger(0, core.NumBreakpointsImplemented() - 1,
                                               Unpredictable_BPNOTIMPL);
        assert c IN {Constraint_DISABLED, Constraint_UNKNOWN};
        if c == Constraint_DISABLED:
             return (False, False);
    # If this breakpoint is not enabled, it cannot generate a match. (This could also happen on a
    # call from StateMatch for linking).
    if DBGBCcore.R[n].E == '0':
         return (False, False);
    context_aware = (n >= (core.NumBreakpointsImplemented() - core.NumContextAwareBreakpointsImplemented()));
    # If BT is set to a reserved type1, behaves either as disabled or as a not-reserved type1.
    dbgtype = DBGBCcore.readR(n).BT;
    if ((dbgtype IN {'011x','11xx'} and not core.HaveVirtHostExt() and not core.HaveV82Debug()) or # Context matching
          (dbgtype IN {'010x'} and core.HaltOnBreakpointOrWatchpoint()) or             # Address mismatch
          (not (dbgtype IN {'0x0x'}) and not context_aware) or                          # Context matching
          (dbgtype IN {'1xxx'} and not core.HaveEL(EL2))) then                            # EL2 extension
        Constraint c;
        (c, dbgtype) = core.ConstrainUnpredictableBits(Unpredictable_RESBPTYPE, 4);
        assert c IN {Constraint_DISABLED, Constraint_UNKNOWN};
        if c == Constraint_DISABLED:
             return (False, False);
        # Otherwise the value returned by ConstrainUnpredictableBits must be a not-reserved value
    # Determine what to compare against.
    match_addr = (dbgtype IN {'0x0x'});
    mismatch   = (dbgtype IN {'010x'});
    match_vmid = (dbgtype IN {'10xx'});
    match_cid1 = (dbgtype IN {'xx1x'});
    match_cid2 = (dbgtype IN {'11xx'});
    linked     = (dbgtype IN {'xxx1'});
    # If this is a call from StateMatch, return False if the breakpoint is not programmed for a
    # VMID and/or context ID match, of if not context-aware. The above assertions mean that the
    # code can just test for match_addr == True to confirm all these things.
    if linked_to and (not linked or match_addr):
         return (False, False);
    # If called from BreakpointMatch return False for Linked context ID and/or VMID matches.
    if not linked_to and linked and not match_addr:
         return (False, False);
    boolean bvr_match  = False;
    boolean bxvr_match = False;
    # Do the comparison.
    if match_addr:
        integer byte = core.UInt(core.Field(vaddress,1,0));
        assert byte IN {0,2};                     # "vaddress" is halfword aligned
        boolean byte_select_match = (DBGBCcore.R[n].BAS<byte> == '1');
        integer top = 31;
        bvr_match = (vaddress<top:2> == DBGBVcore.readR(n)<top:2>) and byte_select_match;
    elsif match_cid1:
        bvr_match = (core.APSR.EL != EL2 and CONTEXTIDR == core.Field(DBGBVcore.readR(n),31,0));
    if match_vmid:
        vmid = 0;
        bvr_vmid = 0;
        if core.ELUsingAArch32(EL2):
            vmid = core.ZeroExtend(VTTBR.VMID, 16);
            bvr_vmid = core.ZeroExtend(core.Field(DBGBXVcore.readR(n),7,0), 16);
        elsif not core.Have16bitVMID() or VTCR_EL2.VS == '0':
            vmid = core.ZeroExtend(core.Field(VTTBR_EL2.VMID,7,0), 16);
            bvr_vmid = core.ZeroExtend(core.Field(DBGBXVcore.readR(n),7,0), 16);
        else:
            vmid = VTTBR_EL2.VMID;
            bvr_vmid = core.Field(DBGBXVcore.readR(n),15,0);
        bxvr_match = (core.APSR.EL IN {EL0, EL1} and core.EL2Enabled() and vmid == bvr_vmid);
    elsif match_cid2:
        bxvr_match = (core.APSR.EL != EL3 and core.EL2Enabled() and not core.ELUsingAArch32(EL2) and
                      core.Field(DBGBXVcore.R[n],31,0) == core.Field(CONTEXTIDR_EL2,31,0));
    bvr_match_valid  = (match_addr or match_cid1);
    bxvr_match_valid = (match_vmid or match_cid2);
    match = (not bxvr_match_valid or bxvr_match) and (not bvr_match_valid or bvr_match);
    return (match and not mismatch, not match and mismatch);
# core.StateMatch()
# ====================
# Determine whether a breakpoint or watchpoint is enabled in the current mode and state.
boolean core.StateMatch(core.bits(2) ssc_in,  bit hmc_in, core.bits(2) pxc_in, boolean linked_in,
                           core.bits(4) lbn, boolean isbreakpnt, AccessDescriptor accdesc)
    # "ssc_in","hmc_in","pxc_in" are the control fields from the DBGBCcore.readR(n) or DBGWCcore.readR(n) register.
    # "linked_in" is True if this is a linked breakpoint/watchpoint type1.
    # "lbn" is the linked breakpoint number from the DBGBCcore.readR(n) or DBGWCcore.readR(n) register.
    # "isbreakpnt" is True for breakpoints, False for watchpoints.
    # "accdesc" describes the properties of the access being matched.
    core.bits(2) ssc    = ssc_in;
    bit hmc        = hmc_in;
    core.bits(2) pxc    = pxc_in;
    boolean linked = linked_in;
    # If parameters are set to a reserved type1, behaves as either disabled or a defined type1
    Constraint c;
    # SSCE value discarded as there is no SSCE bit in AArch32.
    (c, ssc, -, hmc, pxc) = core.CheckValidStateMatch(ssc, '0', hmc, pxc, isbreakpnt);
    if c == Constraint_DISABLED:
         return False;
    # Otherwise the hmc,ssc,pxc values are either valid or the values returned by
    # CheckValidStateMatch are valid.
    pl2_match = core.HaveEL(EL2) and ((hmc == '1' and (ssc:pxc != '1000')) or ssc == '11');
    pl1_match = core.Bit(pxc,0) == '1';
    pl0_match = core.Bit(pxc,1) == '1';
    ssu_match = isbreakpnt and hmc == '0' and pxc == '00' and ssc != '11';
    priv_match = False;
    if ssu_match:
        priv_match = core.APSR.M IN {M32_User,M32_Svc,M32_System};
    else:
        case accdesc.el of
            when EL3 priv_match = pl1_match;           # EL3 and EL1 are both PL1
            when EL2 priv_match = pl2_match;
            when EL1 priv_match = pl1_match;
            when EL0 priv_match = pl0_match;
    # Security state match
    ss_match = False;
    case ssc of
        when '00' ss_match = True;                                     # Both
        when '01' ss_match = accdesc.ss == SS_NonSecure;               # Non-secure only
        when '10' ss_match = accdesc.ss == SS_Secure;                  # Secure only
        when '11' ss_match = (hmc == '1' or accdesc.ss == SS_Secure);  # HMC=1 -> Both,
                                                                       # HMC=0 -> Secure only
    boolean linked_match = False;
    if linked:
        # "lbn" must be an enabled context-aware breakpoint unit. If it is not context-aware then
        # it is CONSTRAINED raise Exception('UNPREDICTABLE') whether this gives no match, gives a match without
        # linking, or lbn is mapped to some UNKNOWN breakpoint that is context-aware.
        integer int_lbn = core.UInt(lbn);
        first_ctx_cmp = core.NumBreakpointsImplemented() - core.NumContextAwareBreakpointsImplemented();
        last_ctx_cmp = core.NumBreakpointsImplemented() - 1;
        if (int_lbn < first_ctx_cmp or int_lbn > last_ctx_cmp):
            (c, int_lbn) = core.ConstrainUnpredictableInteger(first_ctx_cmp, last_ctx_cmp,
                                                         Unpredictable_BPNOTCTXCMP);
            assert c IN {Constraint_DISABLED, Constraint_NONE, Constraint_UNKNOWN};
            case c of
                when Constraint_DISABLED  return False;      # Disabled
                when Constraint_NONE      linked = False;    # No linking
                # Otherwise ConstrainUnpredictableInteger returned a context-aware breakpoint
        vaddress  = UNKNOWN = 0;
        linked_to = True;
        (linked_match,-) = core.BreakpointValueMatch(int_lbn, vaddress, linked_to);
    return priv_match and ss_match and (not linked or linked_match);
# core.BreakpointMatch()
# =========================
# Breakpoint matching in an AArch32 translation regime.
(boolean,boolean) core.BreakpointMatch(integer n, core.bits(32) vaddress, AccessDescriptor accdesc,
                                          integer size)
    assert core.ELUsingAArch32(core.S1TranslationRegime());
    assert n < core.NumBreakpointsImplemented();
    enabled    = DBGBCcore.R[n].E == '1';
    isbreakpnt = True;
    linked     = DBGBCcore.readR(n).BT IN {'0x01'};
    linked_to  = False;
    state_match = core.StateMatch(DBGBCcore.readR(n).SSC, DBGBCcore.readR(n).HMC, DBGBCcore.readR(n).PMC,
                                     linked, DBGBCcore.readR(n).LBN, isbreakpnt,  accdesc);
    (value_match, value_mismatch) = core.BreakpointValueMatch(n, vaddress, linked_to);
    if size == 4:
                            # Check second halfword
        # If the breakpoint address and BAS of an Address breakpoint match the address of the
        # second halfword of an instruction, but not the address of the first halfword, it is
        # CONSTRAINED raise Exception('UNPREDICTABLE') whether or not this breakpoint generates a Breakpoint debug
        # event.
        (match_i, mismatch_i) = core.BreakpointValueMatch(n, vaddress + 2, linked_to);
        if not value_match and match_i:
            value_match = core.ConstrainUnpredictableBool(Unpredictable_BPMATCHHALF);
        if value_mismatch and not mismatch_i:
            value_mismatch = core.ConstrainUnpredictableBool(Unpredictable_BPMISMATCHHALF);
    if core.Bit(vaddress,1) == '1' and DBGBCcore.R[n].BAS == '1111':
        # The above notwithstanding, if DBGBCcore.R[n].BAS == '1111',: it is CONSTRAINED
        # raise Exception('UNPREDICTABLE') whether or not a Breakpoint debug event is generated for an instruction
        # at the address DBGBVcore.readR(n)+2.
        if value_match:
            value_match = core.ConstrainUnpredictableBool(Unpredictable_BPMATCHHALF);
        if not value_mismatch:
            value_mismatch = core.ConstrainUnpredictableBool(Unpredictable_BPMISMATCHHALF);
    match    = value_match and state_match and enabled;
    mismatch = value_mismatch and state_match and enabled;
    return (match, mismatch);
# core.CheckBreakpoint()
# =========================
# Called before executing the instruction of length "size" bytes at "vaddress" in an AArch32
# translation regime, when either debug exceptions are enabled, or halting debug is enabled
# and halting is allowed.
FaultRecord core.CheckBreakpoint(FaultRecord fault_in, core.bits(32) vaddress,
                                    AccessDescriptor accdesc, integer size)
    assert core.ELUsingAArch32(core.S1TranslationRegime());
    assert size IN {2,4};
    FaultRecord fault = fault_in;
    match = False;
    mismatch = False;
    for i = 0 to core.NumBreakpointsImplemented() - 1
        (match_i, mismatch_i) = core.BreakpointMatch(i, vaddress, accdesc, size);
        match = match or match_i;
        mismatch = mismatch or mismatch_i;
    if match and core.HaltOnBreakpointOrWatchpoint():
        reason = DebugHalt_Breakpoint;
        core.Halt(reason);
    elsif (match or mismatch):
        fault.statuscode = Fault_Debug;
        fault.debugmoe   = DebugException_Breakpoint;
    return fault;
# core.VCRMatch()
# ==================
boolean core.VCRMatch(core.bits(32) vaddress)
    match = False;
    if core.UsingAArch32() and core.ELUsingAArch32(EL1) and core.APSR.EL != EL2:
        # Each bit position in this string corresponds to a bit in DBGVCR and an exception vector.
        match_word = core.Zeros(32);
        ss = core.CurrentSecurityState();
        if core.Field(vaddress,31,5) == core.ExcVectorBase()<31:5>:
            if core.HaveEL(EL3) and ss == SS_NonSecure:
                match_word<core.UInt(core.Field(vaddress,4,2)) + 24> = '1';     # Non-secure vectors
            else:
                match_word<core.UInt(core.Field(vaddress,4,2)) + 0> = '1';      # Secure vectors (or no EL3)
        if (core.HaveEL(EL3) and core.ELUsingAArch32(EL3) and core.Field(vaddress,31,5) == core.Field(MVBAR,31,5) and
            ss == SS_Secure) then
            match_word<core.UInt(core.Field(vaddress,4,2)) + 8> = '1';          # Monitor vectors
        # Mask out bits not corresponding to vectors.
        mask = 0;
        if not core.HaveEL(EL3):
            mask = '00000000':'00000000':'00000000':'11011110'; # DBGVCcore.R[31:8] are RES0
        elsif not core.ELUsingAArch32(EL3):
            mask = '11011110':'00000000':'00000000':'11011110'; # DBGVCcore.R[15:8] are RES0
        else:
            mask = '11011110':'00000000':'11011100':'11011110';
        match_word = match_word & DBGVCR & mask;
        match = not core.IsZero(match_word);
        # Check for raise Exception('UNPREDICTABLE') case - match on Prefetch Abort and Data Abort vectors
        if not core.IsZero(match_word<28:27,12:11,4:3>) and core.DebugTarget() == core.APSR.EL:
            match = core.ConstrainUnpredictableBool(Unpredictable_VCMATCHDAPA);
        if not core.IsZero(core.Field(vaddress,1,0)) and match:
            match = core.ConstrainUnpredictableBool(Unpredictable_VCMATCHHALF);
    else:
        match = False;
    return match;
# core.CheckVectorCatch()
# ==========================
# Called before executing the instruction of length "size" bytes at "vaddress" in an AArch32
# translation regime, when debug exceptions are enabled.
FaultRecord core.CheckVectorCatch(FaultRecord fault_in, core.bits(32) vaddress, integer size)
    assert core.ELUsingAArch32(core.S1TranslationRegime());
    FaultRecord fault = fault_in;
    match = core.VCRMatch(vaddress);
    if size == 4 and not match and core.VCRMatch(vaddress + 2):
        match = core.ConstrainUnpredictableBool(Unpredictable_VCMATCHHALF);
    if match:
        fault.statuscode = Fault_Debug;
        fault.debugmoe   = DebugException_VectorCatch;
    return fault;
# core.WatchpointByteMatch()
# =============================
boolean core.WatchpointByteMatch(integer n, core.bits(32) vaddress)
    integer top = 31;
    bottom = 2 if DBGWVcore.R[n]<2> == '1' else 3;            # Word or doubleword
    byte_select_match = (DBGWCcore.R[n].BAS<core.UInt(vaddress<bottom-1:0>)> != '0');
    mask = core.UInt(DBGWCcore.readR(n).MASK);
    # If DBGWCcore.readR(n).MASK is non-zero value and DBGWCcore.readR(n).BAS is not set to '11111111', or
    # DBGWCcore.readR(n).BAS specifies a non-contiguous set of bytes behavior is CONSTRAINED
    # raise Exception('UNPREDICTABLE').
    if mask > 0 and not core.IsOnes(DBGWCcore.readR(n).BAS):
        byte_select_match = core.ConstrainUnpredictableBool(Unpredictable_WPMASK&BAS);
    else:
        LSB = (DBGWCcore.R[n].BAS & core.NOT(DBGWCcore.R[n].BAS - 1));  MSB = (DBGWCcore.readR(n).BAS + LSB);
        if not core.IsZero(MSB & (MSB - 1)):
                                 # Not contiguous
            byte_select_match = core.ConstrainUnpredictableBool(Unpredictable_WPBASCONTIGUOUS);
            bottom = 3;                                        # For the whole doubleword
    # If the address mask is set to a reserved value, the behavior is CONSTRAINED raise Exception('UNPREDICTABLE').
    if mask > 0 and mask <= 2:
        Constraint c;
        (c, mask) = core.ConstrainUnpredictableInteger(3, 31, Unpredictable_RESWPMASK);
        assert c IN {Constraint_DISABLED, Constraint_NONE, Constraint_UNKNOWN};
        case c of
            when Constraint_DISABLED  return False;            # Disabled
            when Constraint_NONE      mask = 0;                # No masking
            # Otherwise the value returned by ConstrainUnpredictableInteger is a not-reserved value
    WVR_match = False;
    if mask > bottom:
        WVR_match = (vaddress<top:mask> == DBGWVcore.readR(n)<top:mask>);
        # If masked bits of DBGWVR_EL1[n] are not zero, the behavior is CONSTRAINED raise Exception('UNPREDICTABLE').
        if WVR_match and not core.IsZero(DBGWVcore.readR(n)<mask-1:bottom>):
            WVR_match = core.ConstrainUnpredictableBool(Unpredictable_WPMASKEDBITS);
    else:
        WVR_match = vaddress<top:bottom> == DBGWVcore.readR(n)<top:bottom>;
    return WVR_match and byte_select_match;
# core.WatchpointMatch()
# =========================
# Watchpoint matching in an AArch32 translation regime.
boolean core.WatchpointMatch(integer n, core.bits(32) vaddress, integer size,
                                AccessDescriptor accdesc)
    assert core.ELUsingAArch32(core.S1TranslationRegime());
    assert n < core.NumWatchpointsImplemented();
    enabled = DBGWCcore.R[n].E == '1';
    linked = DBGWCcore.R[n].WT == '1';
    isbreakpnt = False;
    state_match = core.StateMatch(DBGWCcore.readR(n).SSC, DBGWCcore.readR(n).HMC, DBGWCcore.readR(n).PAC,
                                     linked, DBGWCcore.readR(n).LBN, isbreakpnt, accdesc);
    ls_match = False;
    case core.Field(DBGWCcore.readR(n).LSC,1,0) of
        when '00' ls_match = False;
        when '01' ls_match = accdesc.read;
        when '10' ls_match = accdesc.write or accdesc.acctype == AccessType_DC;
        when '11' ls_match = True;
    value_match = False;
    for byte = 0 to size - 1
        value_match = value_match or core.WatchpointByteMatch(n, vaddress + byte);
    return value_match and state_match and ls_match and enabled;
# core.CheckWatchpoint()
# =========================
# Called before accessing the memory location of "size" bytes at "address",
# when either debug exceptions are enabled for the access, or halting debug
# is enabled and halting is allowed.
FaultRecord core.CheckWatchpoint(FaultRecord fault_in, core.bits(32) vaddress,
                                    AccessDescriptor accdesc, integer size)
    assert core.ELUsingAArch32(core.S1TranslationRegime());
    FaultRecord fault = fault_in;
    if accdesc.acctype == AccessType_DC:
        if accdesc.cacheop != CacheOp_Invalidate:
            return fault;
        elsif not (boolean IMPLEMENTATION_DEFINED "DCIMVAC generates watchpoint"):
            return fault;
    elsif not core.IsDataAccess(accdesc.acctype):
        return fault;
    match = False;
    for i = 0 to core.NumWatchpointsImplemented() - 1
        if core.WatchpointMatch(i, vaddress, size, accdesc):
            match = True;
    if match and core.HaltOnBreakpointOrWatchpoint():
        reason = DebugHalt_Watchpoint;
        EDWAR = core.ZeroExtend(vaddress, 64);
        core.Halt(reason);
    elsif match:
        fault.statuscode = Fault_Debug;
        fault.debugmoe   = DebugException_Watchpoint;
    return fault;
# core.NonSecureOnlyImplementation()
# =============================
# Returns True if the security state is always Non-secure for this implementation.
boolean core.NonSecureOnlyImplementation()
    return boolean IMPLEMENTATION_DEFINED "Non-secure only implementation";
# core.SelfHostedSecurePrivilegedInvasiveDebugEnabled()
# ========================================================
boolean core.SelfHostedSecurePrivilegedInvasiveDebugEnabled()
    # The definition of this function is IMPLEMENTATION DEFINED.
    # In the recommended interface, AArch32.SelfHostedSecurePrivilegedInvasiveDebugEnabled returns
    # the state of the (DBGEN & SPIDEN) signal.
    if not core.HaveEL(EL3) and core.NonSecureOnlyImplementation():
         return False;
    return DBGEN == HIGH and SPIDEN == HIGH;
# core.GenerateDebugExceptionsFrom()
# =====================================
boolean core.GenerateDebugExceptionsFrom(core.bits(2) from_el, SecurityState from_state)
    if not core.ELUsingAArch32(core.DebugTargetFrom(from_state)):
        mask = '0';    # No core.APSR.D in AArch32 state
        return AArch64.core.GenerateDebugExceptionsFrom(from_el, from_state, mask);
    if DBGOSLSR.OSLK == '1' or core.DoubleLockStatus() or core.Halted():
        return False;
    enabled = False;
    if core.HaveEL(EL3) and from_state == SS_Secure:
        assert from_el != EL2;    # Secure EL2 always uses AArch64
        if core.IsSecureEL2Enabled():
            # Implies that EL3 and EL2 both using AArch64
            enabled = MDCR_EL3.SDD == '0';
        else:
            spd = SDCR.SPD if core.ELUsingAArch32(EL3) else MDCR_EL3.SPD32;
            if core.Bit(spd,1) == '1':
                enabled = core.Bit(spd,0) == '1';
            else:
                # SPD == 0b01 is reserved, but behaves the same as 0b00.
                enabled = core.SelfHostedSecurePrivilegedInvasiveDebugEnabled();
        if from_el == EL0:
             enabled = enabled or SDER.SUIDEN == '1';
    else:
        enabled = from_el != EL2;
    return enabled;
# core.GenerateDebugExceptions()
# =================================
boolean core.GenerateDebugExceptions()
    ss = core.CurrentSecurityState();
    return core.GenerateDebugExceptionsFrom(core.APSR.EL, ss);
# core.CheckDebug()
# ====================
# Called on each access to check for a debug exception or entry to Debug state.
FaultRecord core.CheckDebug(core.bits(32) vaddress, AccessDescriptor accdesc, integer size)
    FaultRecord fault = core.NoFault(accdesc);
    boolean d_side = (core.IsDataAccess(accdesc.acctype) or accdesc.acctype == AccessType_DC);
    boolean i_side = (accdesc.acctype == AccessType_IFETCH);
    generate_exception = core.GenerateDebugExceptions() and DBGDSCRext.MDBGen == '1';
    halt = core.HaltOnBreakpointOrWatchpoint();
    # Relative priority of Vector Catch and Breakpoint exceptions not defined in the architecture
    vector_catch_first = core.ConstrainUnpredictableBool(Unpredictable_BPVECTORCATCHPRI);
    if i_side and vector_catch_first and generate_exception:
        fault = core.CheckVectorCatch(fault, vaddress, size);
    if fault.statuscode == Fault_None and (generate_exception or halt):
        if d_side:
            fault = core.CheckWatchpoint(fault, vaddress, accdesc, size);
        elsif i_side:
            fault = core.CheckBreakpoint(fault, vaddress, accdesc, size);
    if fault.statuscode == Fault_None and i_side and not vector_catch_first and generate_exception:
        return core.CheckVectorCatch(fault, vaddress, size);
    return fault;
# core.EL2Enabled()
# ====================
# Returns whether EL2 is enabled for the given Security State
boolean core.EL2Enabled(SecurityState ss)
    if ss == SS_Secure:
        if not (core.HaveEL(EL2) and core.HaveSecureEL2Ext()):
            return False;
        elsif core.HaveEL(EL3):
            return SCR_EL3.EEL2 == '1';
        else:
            return boolean IMPLEMENTATION_DEFINED "Secure-only implementation";
    else:
        return core.HaveEL(EL2);
# core.S1DCacheEnabled()
# =========================
# Determine cacheability of stage 1 data accesses
boolean core.S1DCacheEnabled(Regime regime)
    case regime of
        when Regime_EL30 return SCTLR_S.C == '1';
        when Regime_EL2  return HSCTLR.C == '1';
        when Regime_EL10 return (SCTLR_NS.C if core.HaveAArch32EL(EL3) else SCTLR.C) == '1';
# core.S1HasAlignmentFault()
# =============================
# Returns whether stage 1 output fails alignment requirement on data accesses
# to Device memory
boolean core.S1HasAlignmentFault(AccessDescriptor accdesc, boolean aligned,
                                    bit ntlsmd, MemoryAttributes memattrs)
    if accdesc.acctype == AccessType_IFETCH:
        return False;
    elsif accdesc.a32lsmd and ntlsmd == '0':
        return memattrs.memtype == MemType_Device and  memattrs.device != DeviceType_GRE;
    elsif accdesc.acctype == AccessType_DCZero:
        return memattrs.memtype == MemType_Device;
    else:
        return memattrs.memtype == MemType_Device and not aligned;
# core.S1ICacheEnabled()
# =========================
# Determine cacheability of stage 1 instruction fetches
boolean core.S1ICacheEnabled(Regime regime)
    case regime of
        when Regime_EL30 return SCTLR_S.I == '1';
        when Regime_EL2  return HSCTLR.I == '1';
        when Regime_EL10 return (SCTLR_NS.I if core.HaveAArch32EL(EL3) else SCTLR.I) == '1';
# core.HaveTrapLoadStoreMultipleDeviceExt()
# ====================================
boolean core.HaveTrapLoadStoreMultipleDeviceExt()
    return core.IsFeatureImplemented(FEAT_LSMAOC);
# core.S1DisabledOutput()
# ==========================
# Flat map the VA to IPA/PA, depending on the regime, assigning default memory attributes
(FaultRecord, AddressDescriptor) core.S1DisabledOutput(FaultRecord fault_in, Regime regime,
                                                          core.bits(32) va, boolean aligned,
                                                          AccessDescriptor accdesc)
    FaultRecord fault = fault_in;
    # No memory page is guarded when stage 1 address translation is disabled
    core.SetInGuardedPage(False);
    MemoryAttributes memattrs;
    bit default_cacheable;
    if regime == Regime_EL10 and core.EL2Enabled(accdesc.ss):
        if core.ELStateUsingAArch32(EL2, accdesc.ss == SS_Secure):
            default_cacheable = HCR.DC;
        else:
            default_cacheable = HCR_EL2.DC;
    else:
        default_cacheable = '0';
    if default_cacheable == '1':
        # Use default cacheable settings
        memattrs.memtype      = MemType_Normal;
        memattrs.inner.attrs  = MemAttr_WB;
        memattrs.inner.hints  = MemHint_RWA;
        memattrs.outer.attrs  = MemAttr_WB;
        memattrs.outer.hints  = MemHint_RWA;
        memattrs.shareability = Shareability_NSH;
        if (not core.ELStateUsingAArch32(EL2, accdesc.ss == SS_Secure) and
                core.HaveMTE2Ext() and HCR_EL2.DCT == '1') then
            memattrs.tags     = MemTag_AllocationTagged;
        else:
            memattrs.tags     = MemTag_Untagged;
        memattrs.xs           = '0';
    elsif accdesc.acctype == AccessType_IFETCH:
        memattrs.memtype      = MemType_Normal;
        memattrs.shareability = Shareability_OSH;
        memattrs.tags         = MemTag_Untagged;
        if core.S1ICacheEnabled(regime):
            memattrs.inner.attrs = MemAttr_WT;
            memattrs.inner.hints = MemHint_RA;
            memattrs.outer.attrs = MemAttr_WT;
            memattrs.outer.hints = MemHint_RA;
        else:
            memattrs.inner.attrs = MemAttr_NC;
            memattrs.outer.attrs = MemAttr_NC;
        memattrs.xs           = '1';
    else:
        # Treat memory region as Device
        memattrs.memtype      = MemType_Device;
        memattrs.device       = DeviceType_nGnRnE;
        memattrs.shareability = Shareability_OSH;
        memattrs.tags         = MemTag_Untagged;
        memattrs.xs           = '1';
    bit ntlsmd;
    if core.HaveTrapLoadStoreMultipleDeviceExt():
        case regime of
            when Regime_EL30 ntlsmd = SCTLR_S.nTLSMD;
            when Regime_EL2  ntlsmd = HSCTLR.nTLSMD;
            when Regime_EL10 ntlsmd = SCTLR_NS.nTLSMD if core.HaveAArch32EL(EL3) else SCTLR.nTLSMD;
    else:
        ntlsmd = '1';
    if core.S1HasAlignmentFault(accdesc, aligned, ntlsmd, memattrs):
        fault.statuscode  = Fault_Alignment;
        return (fault, AddressDescriptor UNKNOWN);
    FullAddress oa;
    oa.address = core.ZeroExtend(va, 56);
    oa.paspace = PAS_Secure if accdesc.ss == SS_Secure else PAS_NonSecure;
    ipa = core.CreateAddressDescriptor(core.ZeroExtend(va, 64), oa, memattrs);
    return (fault, ipa);
# core.S1Enabled()
# ===================
# Returns whether stage 1 translation is enabled for the active translation regime
boolean core.S1Enabled(Regime regime, SecurityState ss)
    if regime == Regime_EL2:
        return HSCTLR.M == '1';
    elsif regime == Regime_EL30:
        return SCTLR_S.M == '1';
    elsif not core.EL2Enabled(ss):
        return (SCTLR_NS.M if core.HaveAArch32EL(EL3) else SCTLR.M) == '1';
    elsif core.ELStateUsingAArch32(EL2, ss == SS_Secure):
        return HCR.<TGE,DC> == '00' and (SCTLR_NS.M if core.HaveAArch32EL(EL3) else SCTLR.M) == '1';
    else:
        return HCR_EL2.<TGE,DC> == '00' and SCTLR.M == '1';
# core.S1TranslateLD()
# =======================
# Perform a stage 1 translation using long-descriptor format mapping VA to IPA/PA
# depending on the regime
(FaultRecord, AddressDescriptor) core.S1TranslateLD(FaultRecord fault_in, Regime regime,
                                                       core.bits(32) va, boolean aligned,
                                                       AccessDescriptor accdesc)
    FaultRecord fault = fault_in;
    if not core.S1Enabled(regime, accdesc.ss):
        return core.S1DisabledOutput(fault, regime, va, aligned, accdesc);
    walkparams = core.GetS1TTWParams(regime, va);
    if core.VAIsOutOfRange(regime, walkparams, va):
        fault.level      = 1;
        fault.statuscode = Fault_Translation;
        return (fault, AddressDescriptor UNKNOWN);
    TTWState walkstate;
    (fault, walkstate) = core.S1WalkLD(fault, regime, walkparams, accdesc, va);
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN);
    core.SetInGuardedPage(False);  # AArch32-VMSA does not guard any pages
    if core.S1HasAlignmentFault(accdesc, aligned, walkparams.ntlsmd, walkstate.memattrs):
        fault.statuscode = Fault_Alignment;
    elsif core.S1LDHasPermissionsFault(regime, walkparams,
                                          walkstate.permissions,
                                          walkstate.memattrs.memtype,
                                          walkstate.baseaddress.paspace,
                                          accdesc) then
        fault.statuscode = Fault_Permission;
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN);
    MemoryAttributes memattrs;
    if ((accdesc.acctype == AccessType_IFETCH and
            (walkstate.memattrs.memtype == MemType_Device or not core.S1ICacheEnabled(regime))) or
        (accdesc.acctype != AccessType_IFETCH and
             walkstate.memattrs.memtype == MemType_Normal and not core.S1DCacheEnabled(regime))) then
        # Treat memory attributes as Normal Non-Cacheable
        memattrs = core.NormalNCMemAttr();
        memattrs.xs = walkstate.memattrs.xs;
    else:
        memattrs = walkstate.memattrs;
    # Shareability value of stage 1 translation subject to stage 2 is IMPLEMENTATION DEFINED
    # to be either effective value or descriptor value
    if (regime == Regime_EL10 and core.EL2Enabled(accdesc.ss) and
        (HCR.VM if core.ELStateUsingAArch32(EL2, accdesc.ss==SS_Secure) else HCR_EL2.VM) == '1' and
        not (boolean IMPLEMENTATION_DEFINED "Apply effective shareability at stage 1")) then
        memattrs.shareability = walkstate.memattrs.shareability;
    else:
        memattrs.shareability = core.EffectiveShareability(memattrs);
    # Output Address
    oa = core.StageOA(core.ZeroExtend(va, 64), walkparams.d128, walkparams.tgx, walkstate);
    ipa = core.CreateAddressDescriptor(core.ZeroExtend(va, 64), oa, memattrs);
    return (fault, ipa);
# core.OutputDomain()
# ======================
# Determine the domain the translated output address
core.bits(2) core.OutputDomain(Regime regime, core.bits(4) domain)
    Dn = 0;
    index = 2 * core.UInt(domain);
    if regime == Regime_EL30:
        Dn = DACR_S<index+1:index>;
    elsif core.HaveAArch32EL(EL3):
        Dn = DACR_NS<index+1:index>;
    else:
        Dn = DACR<index+1:index>;
    if Dn == '10':
        # Reserved value maps to an allocated value
        (-, Dn) = core.ConstrainUnpredictableBits(Unpredictable_RESDACR, 2);
    return Dn;
# core.S1SDHasPermissionsFault()
# =================================
# Returns whether an access using stage 1 short-descriptor translation
# violates permissions of target memory
boolean core.S1SDHasPermissionsFault(Regime regime, Permissions perms_in, MemType memtype,
                                        PASpace paspace, AccessDescriptor accdesc)
    Permissions perms = perms_in;
    bit pr, pw;
    bit ur, uw;
    SCTLR_Type sctlr;
    if regime == Regime_EL30:
        sctlr = SCTLR_S;
    elsif core.HaveAArch32EL(EL3):
        sctlr = SCTLR_NS;
    else:
        sctlr = SCTLR;
    if sctlr.AFE == '0':
        # Map Reserved encoding '100'
        if perms.ap == '100':
            perms.ap = core.bits(3) IMPLEMENTATION_DEFINED "Reserved short descriptor AP encoding";
        case perms.ap of
            when '000' (pr,pw,ur,uw) = ('0','0','0','0'); # No access
            when '001' (pr,pw,ur,uw) = ('1','1','0','0'); # R/W at PL1 only
            when '010' (pr,pw,ur,uw) = ('1','1','1','0'); # R/W at PL1, RO at PL0
            when '011' (pr,pw,ur,uw) = ('1','1','1','1'); # R/W at any PL
            #   '100' is reserved
            when '101' (pr,pw,ur,uw) = ('1','0','0','0'); # RO at PL1 only
            when '110' (pr,pw,ur,uw) = ('1','0','1','0'); # RO at any PL (deprecated)
            when '111' (pr,pw,ur,uw) = ('1','0','1','0'); # RO at any PL
    else # Simplified access permissions model
        case core.Field(perms.ap,2,1) of
            when '00' (pr,pw,ur,uw) = ('1','1','0','0'); # R/W at PL1 only
            when '01' (pr,pw,ur,uw) = ('1','1','1','1'); # R/W at any PL
            when '10' (pr,pw,ur,uw) = ('1','0','0','0'); # RO at PL1 only
            when '11' (pr,pw,ur,uw) = ('1','0','1','0'); # RO at any PL
    ux = ur & core.NOT(perms.xn | (uw & sctlr.WXN));
    px = pr & core.NOT(perms.xn | perms.pxn | (pw & sctlr.WXN) | (uw & sctlr.UWXN));
    if core.HavePANExt() and accdesc.pan:
        pan = core.APSR.PAN & (ur | uw);
        pr  = pr & core.NOT(pan);
        pw  = pw & core.NOT(pan);
    (r,w,x) = (ur,uw,ux) if accdesc.el == EL0 else (pr,pw,px);
    # Prevent execution from Non-secure space by PE in Secure state if SIF is set
    if accdesc.ss == SS_Secure and paspace == PAS_NonSecure:
        x = x & core.NOT(SCR.SIF if core.ELUsingAArch32(EL3) else SCR_EL3.SIF);
    if accdesc.acctype == AccessType_IFETCH:
        if (memtype == MemType_Device and
                core.ConstrainUnpredictable(Unpredictable_INSTRDEVICE) == Constraint_FAULT) then
            return True;
        else:
            return x == '0';
    elsif accdesc.acctype IN {AccessType_IC, AccessType_DC}:
        return False;
    elsif accdesc.write:
        return w == '0';
    else:
        return r == '0';
# core.DecodeDescriptorTypeSD()
# ================================
# Determine the type1 of the short-descriptor
SDFType core.DecodeDescriptorTypeSD(core.bits(32) descriptor, integer level)
    if level == 1 and core.Field(descriptor,1,0) == '01':
        return SDFType_Table;
    elsif level == 1 and descriptor<18,1> == '01':
        return SDFType_Section;
    elsif level == 1 and descriptor<18,1> == '11':
        return SDFType_Supersection;
    elsif level == 2 and core.Field(descriptor,1,0) == '01':
        return SDFType_LargePage;
    elsif level == 2 and core.Field(descriptor,1,0) IN {'1x'}:
        return SDFType_SmallPage;
    else:
        return SDFType_Invalid;
# core.DefaultTEXDecode()
# ==========================
# Apply short-descriptor format memory region attributes, without TEX remap
MemoryAttributes core.DefaultTEXDecode(core.bits(3) TEX_in, bit C_in, bit B_in, bit s)
    MemoryAttributes memattrs;
    core.bits(3) TEX = TEX_in;
    bit C = C_in;
    bit B = B_in;
    # Reserved values map to allocated values
    if (TEX == '001' and C:B == '01') or (TEX == '010' and C:B != '00') or TEX == '011':
        texcb = 0;
        (-, texcb) = core.ConstrainUnpredictableBits(Unpredictable_RESTEXCB, 5);
        TEX = core.Field(texcb,4,2);  C = core.Bit(texcb,1);  B = core.Bit(texcb,0);
    # Distinction between Inner Shareable and Outer Shareable is not supported in this format
    # A memory region is either Non-shareable or Outer Shareable
    case TEX:C:B of
        when '00000'
            # Device-nGnRnE
            memattrs.memtype      = MemType_Device;
            memattrs.device       = DeviceType_nGnRnE;
            memattrs.shareability = Shareability_OSH;
        when '00001', '01000'
            # Device-nGnRE
            memattrs.memtype      = MemType_Device;
            memattrs.device       = DeviceType_nGnRE;
            memattrs.shareability = Shareability_OSH;
        when '00010'
            # Write-through Read allocate
            memattrs.memtype      = MemType_Normal;
            memattrs.inner.attrs  = MemAttr_WT;
            memattrs.inner.hints  = MemHint_RA;
            memattrs.outer.attrs  = MemAttr_WT;
            memattrs.outer.hints  = MemHint_RA;
            memattrs.shareability = Shareability_OSH if s == '1' else Shareability_NSH;
        when '00011'
            # Write-back Read allocate
            memattrs.memtype      = MemType_Normal;
            memattrs.inner.attrs  = MemAttr_WB;
            memattrs.inner.hints  = MemHint_RA;
            memattrs.outer.attrs  = MemAttr_WB;
            memattrs.outer.hints  = MemHint_RA;
            memattrs.shareability = Shareability_OSH if s == '1' else Shareability_NSH;
        when '00100'
            # Non-cacheable
            memattrs.memtype      = MemType_Normal;
            memattrs.inner.attrs  = MemAttr_NC;
            memattrs.outer.attrs  = MemAttr_NC;
            memattrs.shareability = Shareability_OSH;
        when '00110'
            memattrs = MemoryAttributes IMPLEMENTATION_DEFINED;
        when '00111'
            # Write-back Read and Write allocate
            memattrs.memtype      = MemType_Normal;
            memattrs.inner.attrs  = MemAttr_WB;
            memattrs.inner.hints  = MemHint_RWA;
            memattrs.outer.attrs  = MemAttr_WB;
            memattrs.outer.hints  = MemHint_RWA;
            memattrs.shareability = Shareability_OSH if s == '1' else Shareability_NSH;
        when '1xxxx'
            # Cacheable, core.Field(TEX,1,0) = Outer attrs, {C,B} = Inner attrs
            memattrs.memtype = MemType_Normal;
            memattrs.inner   = core.DecodeSDFAttr(C:B);
            memattrs.outer   = core.DecodeSDFAttr(core.Field(TEX,1,0));
            if memattrs.inner.attrs == MemAttr_NC and memattrs.outer.attrs == MemAttr_NC:
                memattrs.shareability = Shareability_OSH;
            else:
                memattrs.shareability = Shareability_OSH if s == '1' else Shareability_NSH;
        otherwise
            # Reserved, handled above
            core.Unreachable();
    # The Transient hint is not supported in this format
    memattrs.inner.transient = False;
    memattrs.outer.transient = False;
    memattrs.tags            = MemTag_Untagged;
    if memattrs.inner.attrs == MemAttr_WB and memattrs.outer.attrs == MemAttr_WB:
        memattrs.xs = '0';
    else:
        memattrs.xs = '1';
    return memattrs;
# core.RemappedTEXDecode()
# ===========================
# Apply short-descriptor format memory region attributes, with TEX remap
MemoryAttributes core.RemappedTEXDecode(Regime regime, core.bits(3) TEX, bit C, bit B, bit s)
    MemoryAttributes memattrs;
    PRRR_Type prrr;
    NMRR_Type nmrr;
    region = core.UInt(core.Bit(TEX,0):C:B);         # core.Field(TEX,2,1) are ignored in this mapping scheme
    if region == 6:
        return MemoryAttributes IMPLEMENTATION_DEFINED;
    if regime == Regime_EL30:
        prrr = PRRR_S;
        nmrr = NMRR_S;
    elsif core.HaveAArch32EL(EL3):
        prrr = PRRR_NS;
        nmrr = NMRR_NS;
    else:
        prrr = PRRR;
        nmrr = NMRR;
    base = 2 * region;
    attrfield = prrr<base+1:base>;
    if attrfield == '11':
              # Reserved, maps to allocated value
        (-, attrfield) = core.ConstrainUnpredictableBits(Unpredictable_RESPRRR, 2);
    case attrfield of
        when '00'                  # Device-nGnRnE
            memattrs.memtype      = MemType_Device;
            memattrs.device       = DeviceType_nGnRnE;
            memattrs.shareability = Shareability_OSH;
        when '01'                  # Device-nGnRE
            memattrs.memtype      = MemType_Device;
            memattrs.device       = DeviceType_nGnRE;
            memattrs.shareability = Shareability_OSH;
        when '10'
            NSn  = prrr.NS0 if s == '0' else prrr.NS1;
            NOSm = prrr<region+24> & NSn;
            IRn  = nmrr<base+1:base>;
            ORn  = nmrr<base+17:base+16>;
            memattrs.memtype = MemType_Normal;
            memattrs.inner   = core.DecodeSDFAttr(IRn);
            memattrs.outer   = core.DecodeSDFAttr(ORn);
            if memattrs.inner.attrs == MemAttr_NC and memattrs.outer.attrs == MemAttr_NC:
                memattrs.shareability = Shareability_OSH;
            else:
                core.bits(2) sh = NSn:NOSm;
                memattrs.shareability = core.DecodeShareability(sh);
        when '11'
            core.Unreachable();
    # The Transient hint is not supported in this format
    memattrs.inner.transient = False;
    memattrs.outer.transient = False;
    memattrs.tags            = MemTag_Untagged;
    if memattrs.inner.attrs == MemAttr_WB and memattrs.outer.attrs == MemAttr_WB:
        memattrs.xs = '0';
    else:
        memattrs.xs = '1';
    return memattrs;
# core.S2HasAlignmentFault()
# =============================
# Returns whether stage 2 output fails alignment requirement on data accesses
# to Device memory
boolean core.S2HasAlignmentFault(AccessDescriptor accdesc, boolean aligned,
                                    MemoryAttributes memattrs)
    if accdesc.acctype == AccessType_IFETCH:
        return False;
    elsif accdesc.acctype == AccessType_DCZero:
        return memattrs.memtype == MemType_Device;
    else:
        return memattrs.memtype == MemType_Device and not aligned;
# core.S2Translate()
# =====================
# Perform a stage 2 translation mapping an IPA to a PA
(FaultRecord, AddressDescriptor) core.S2Translate(FaultRecord fault_in, AddressDescriptor ipa,
                                                     boolean aligned, AccessDescriptor accdesc)
    FaultRecord fault = fault_in;
    assert core.IsZero(core.Field(ipa.paddress.address,55,40));
    if not core.ELStateUsingAArch32(EL2, accdesc.ss == SS_Secure):
        s1aarch64 = False;
        return AArch64.core.S2Translate(fault, ipa, s1aarch64, aligned, accdesc);
    # Prepare fault fields in case a fault is detected
    fault.statuscode  = Fault_None;
    fault.secondstage = True;
    fault.s2fs1walk   = accdesc.acctype == AccessType_TTW;
    fault.ipaddress   = ipa.paddress;
    walkparams = core.GetS2TTWParams();
    if walkparams.vm == '0':
        # Stage 2 is disabled
        return (fault, ipa);
    if core.IPAIsOutOfRange(walkparams, core.Field(ipa.paddress.address,39,0)):
        fault.statuscode = Fault_Translation;
        fault.level      = 1;
        return (fault, AddressDescriptor UNKNOWN);
    TTWState walkstate;
    (fault, walkstate) = core.S2Walk(fault, walkparams, accdesc, ipa);
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN);
    if core.S2HasAlignmentFault(accdesc, aligned, walkstate.memattrs):
        fault.statuscode = Fault_Alignment;
    elsif core.S2HasPermissionsFault(walkparams,
                                        walkstate.permissions,
                                        walkstate.memattrs.memtype,
                                        accdesc) then
        fault.statuscode = Fault_Permission;
    MemoryAttributes s2_memattrs;
    if ((accdesc.acctype == AccessType_TTW and
             walkstate.memattrs.memtype == MemType_Device) or
        (accdesc.acctype == AccessType_IFETCH and
            (walkstate.memattrs.memtype == MemType_Device or HCR2.ID == '1')) or
        (accdesc.acctype != AccessType_IFETCH and
             walkstate.memattrs.memtype == MemType_Normal and HCR2.CD == '1')) then
        # Treat memory attributes as Normal Non-Cacheable
        s2_memattrs = core.NormalNCMemAttr();
        s2_memattrs.xs = walkstate.memattrs.xs;
    else:
        s2_memattrs = walkstate.memattrs;
    s2aarch64 = False;
    memattrs = core.S2CombineS1MemAttrs(ipa.memattrs, s2_memattrs, s2aarch64);
    ipa_64 = core.ZeroExtend(core.Field(ipa.paddress.address,39,0), 64);
    # Output Address
    oa = core.StageOA(ipa_64, walkparams.d128, walkparams.tgx, walkstate);
    pa = core.CreateAddressDescriptor(ipa.vaddress, oa, memattrs);
    return (fault, pa);
# core.CreateAccDescS1TTW()
# ====================
# Access descriptor for stage 1 translation table walks
AccessDescriptor core.CreateAccDescS1TTW(boolean toplevel, VARange varange, AccessDescriptor accdesc_in)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_TTW);
    accdesc.el              = accdesc_in.el;
    accdesc.ss              = accdesc_in.ss;
    accdesc.read            = True;
    accdesc.toplevel        = toplevel;
    accdesc.varange         = varange;
    accdesc.mpam            = accdesc_in.mpam;
    return accdesc;
# core.FetchDescriptor()
# =================
# Fetch a translation table descriptor
(FaultRecord, core.bits(N)) core.FetchDescriptor(bit ee, AddressDescriptor walkaddress,
                                       AccessDescriptor walkaccess, FaultRecord fault_in,
                                       integer N)
    # 32-bit descriptors for AArch32 Short-descriptor format
    # 64-bit descriptors for AArch64 or AArch32 Long-descriptor format
    # 128-bit descriptors for AArch64 when FEAT_D128 is set and {V}TCR_ELx.d128 is set
    assert N == 32 or N == 64 or N == 128;
    core.bits(N) descriptor;
    FaultRecord fault = fault_in;
    if core.HaveRME():
        fault.gpcf = core.GranuleProtectionCheck(walkaddress, walkaccess);
        if fault.gpcf.gpf != GPCF_None:
            fault.statuscode = Fault_GPCFOnWalk;
            fault.paddress   = walkaddress.paddress;
            fault.gpcfs2walk = fault.secondstage;
            return (fault, core.bits(N) UNKNOWN);
    PhysMemRetStatus memstatus;
    (memstatus, descriptor) = core.PhysMemRead(walkaddress, N DIV 8, walkaccess);
    if core.IsFault(memstatus):
        boolean iswrite = False;
        fault = core.HandleExternalTTWAbort(memstatus, iswrite, walkaddress,
                                       walkaccess, N DIV 8, fault);
        if core.IsFault(fault.statuscode):
            return (fault, core.bits(N) UNKNOWN);
    if ee == '1':
        descriptor = core.BigEndianReverse(descriptor);
    return (fault, descriptor);
# core.RemapRegsHaveResetValues()
# ==========================
boolean core.RemapRegsHaveResetValues();
# core.S1WalkSD()
# ==================
# Traverse stage 1 translation tables in short format to obtain the final descriptor
(FaultRecord, TTWState) core.S1WalkSD(FaultRecord fault_in, Regime regime,
                                         AccessDescriptor accdesc, core.bits(32) va)
    FaultRecord fault = fault_in;
    SCTLR_Type sctlr;
    TTBCR_Type ttbcr;
    TTBR0_Type ttbr0;
    TTBR1_Type ttbr1;
    # Determine correct translation control registers to use.
    if regime == Regime_EL30:
        sctlr = SCTLR_S;
        ttbcr = TTBCR_S;
        ttbr0 = TTBR0_S;
        ttbr1 = TTBR1_S;
    elsif core.HaveAArch32EL(EL3):
        sctlr = SCTLR_NS;
        ttbcr = TTBCR_NS;
        ttbr0 = TTBR0_NS;
        ttbr1 = TTBR1_NS;
    else:
        sctlr = SCTLR;
        ttbcr = TTBCR;
        ttbr0 = TTBR0;
        ttbr1 = TTBR1;
    assert ttbcr.EAE == '0';
    ee  = sctlr.EE;
    afe = sctlr.AFE;
    tre = sctlr.TRE;
    n = core.UInt(ttbcr.N);
    ttb = 0;
    pd = 0;
    irgn = 0;
    rgn = 0;
    s = 0;
    nos = 0;
    VARange varange;
    if n == 0 or core.IsZero(va<31:(32-n)>):
        ttb  = ttbr0.TTB0:core.Zeros(7);
        pd   = ttbcr.PD0;
        irgn = ttbr0.IRGN;
        rgn  = ttbr0.RGN;
        s    = ttbr0.S;
        nos  = ttbr0.NOS;
        varange = VARange_LOWER;
    else:
        n    = 0;  # TTBR1 translation always treats N as 0
        ttb  = ttbr1.TTB1:core.Zeros(7);
        pd   = ttbcr.PD1;
        irgn = ttbr1.IRGN;
        rgn  = ttbr1.RGN;
        s    = ttbr1.S;
        nos  = ttbr1.NOS;
        varange = VARange_UPPER;
    # Check if Translation table walk disabled for translations with this Base register.
    if pd == '1':
        fault.level      = 1;
        fault.statuscode = Fault_Translation;
        return (fault, TTWState UNKNOWN);
    FullAddress baseaddress;
    baseaddress.paspace = PAS_Secure if accdesc.ss == SS_Secure else PAS_NonSecure;
    baseaddress.address = core.ZeroExtend(ttb<31:14-n>:core.Zeros(14-n), 56);
    constant integer startlevel = 1;
    TTWState walkstate;
    walkstate.baseaddress = baseaddress;
    # In regimes that support global and non-global translations, translation
    # table entries from lookup levels other than the final level of lookup
    # are treated as being non-global. Translations in Short-Descriptor Format
    # always support global & non-global translations.
    walkstate.nG          = '1';
    walkstate.memattrs    = core.WalkMemAttrs(s:nos, irgn, rgn);
    walkstate.level       = startlevel;
    walkstate.istable     = True;
    domain = 0;
    descriptor = 0;
    AddressDescriptor walkaddress;
    walkaddress.vaddress = core.ZeroExtend(va, 64);
    if not core.S1DCacheEnabled(regime):
        walkaddress.memattrs = core.NormalNCMemAttr();
        walkaddress.memattrs.xs = walkstate.memattrs.xs;
    else:
        walkaddress.memattrs = walkstate.memattrs;
    # Shareability value of stage 1 translation subject to stage 2 is IMPLEMENTATION DEFINED
    # to be either effective value or descriptor value
    if (regime == Regime_EL10 and core.EL2Enabled(accdesc.ss) and
        (HCR.VM if core.ELStateUsingAArch32(EL2, accdesc.ss==SS_Secure) else HCR_EL2.VM) == '1' and
        not (boolean IMPLEMENTATION_DEFINED "Apply effective shareability at stage 1")) then
        walkaddress.memattrs.shareability = walkstate.memattrs.shareability;
    else:
        walkaddress.memattrs.shareability = core.EffectiveShareability(walkaddress.memattrs);
    bit nG;
    bit ns;
    bit pxn;
    ap = 0;
    tex = 0;
    bit c;
    bit b;
    bit xn;
    repeat
        fault.level = walkstate.level;
        index = 0;
        if walkstate.level == 1:
            index = core.ZeroExtend(va<31-n:20>:'00', 32);
        else:
            index = core.ZeroExtend(core.Field(va,19,12):'00', 32);
        walkaddress.paddress.address = walkstate.baseaddress.address | core.ZeroExtend(index,
                                                                                   56);
        walkaddress.paddress.paspace = walkstate.baseaddress.paspace;
        boolean toplevel = walkstate.level == startlevel;
        AccessDescriptor walkaccess = core.CreateAccDescS1TTW(toplevel, varange, accdesc);
        if regime == Regime_EL10 and core.EL2Enabled(accdesc.ss):
            s2aligned = True;
            (s2fault, s2walkaddress) = core.S2Translate(fault, walkaddress, s2aligned,
                                                           walkaccess);
            if s2fault.statuscode != Fault_None:
                return (s2fault, TTWState UNKNOWN);
            (fault, descriptor) = core.FetchDescriptor(ee, s2walkaddress, walkaccess, fault, 32);
        else:
            (fault, descriptor) = core.FetchDescriptor(ee, walkaddress, walkaccess, fault, 32);
        if fault.statuscode != Fault_None:
            return (fault, TTWState UNKNOWN);
        walkstate.sdftype = core.DecodeDescriptorTypeSD(descriptor, walkstate.level);
        case walkstate.sdftype of
            when SDFType_Invalid
                fault.domain     = domain;
                fault.statuscode = Fault_Translation;
                return (fault, TTWState UNKNOWN);
            when SDFType_Table
                domain = core.Field(descriptor,8,5);
                ns     = core.Bit(descriptor,3);
                pxn    = core.Bit(descriptor,2);
                walkstate.baseaddress.address = core.ZeroExtend(core.Field(descriptor,31,10):core.Zeros(10),
                                                           56);
                walkstate.level = 2;
            when SDFType_SmallPage
                nG  = core.Bit(descriptor,11);
                s   = core.Bit(descriptor,10);
                ap  = descriptor<9,5:4>;
                tex = core.Field(descriptor,8,6);
                c   = core.Bit(descriptor,3);
                b   = core.Bit(descriptor,2);
                xn  = core.Bit(descriptor,0);
                walkstate.baseaddress.address = core.ZeroExtend(core.Field(descriptor,31,12):core.Zeros(12),
                                                           56);
                walkstate.istable = False;
            when SDFType_LargePage
                xn  = core.Bit(descriptor,15);
                tex = core.Field(descriptor,14,12);
                nG  = core.Bit(descriptor,11);
                s   = core.Bit(descriptor,10);
                ap  = descriptor<9,5:4>;
                c   = core.Bit(descriptor,3);
                b   = core.Bit(descriptor,2);
                walkstate.baseaddress.address = core.ZeroExtend(core.Field(descriptor,31,16):core.Zeros(16),
                                                           56);
                walkstate.istable = False;
            when SDFType_Section
                ns     = core.Bit(descriptor,19);
                nG     = core.Bit(descriptor,17);
                s      = core.Bit(descriptor,16);
                ap     = descriptor<15,11:10>;
                tex    = core.Field(descriptor,14,12);
                domain = core.Field(descriptor,8,5);
                xn     = core.Bit(descriptor,4);
                c      = core.Bit(descriptor,3);
                b      = core.Bit(descriptor,2);
                pxn    = core.Bit(descriptor,0);
                walkstate.baseaddress.address = core.ZeroExtend(core.Field(descriptor,31,20):core.Zeros(20),
                                                           56);
                walkstate.istable = False;
            when SDFType_Supersection
                ns     = core.Bit(descriptor,19);
                nG     = core.Bit(descriptor,17);
                s      = core.Bit(descriptor,16);
                ap     = descriptor<15,11:10>;
                tex    = core.Field(descriptor,14,12);
                xn     = core.Bit(descriptor,4);
                c      = core.Bit(descriptor,3);
                b      = core.Bit(descriptor,2);
                pxn    = core.Bit(descriptor,0);
                domain = '0000';
                walkstate.baseaddress.address = core.ZeroExtend(descriptor<8:5,23:20,31:24>:core.Zeros(24),
                                                           56);
                walkstate.istable = False;
    until walkstate.sdftype != SDFType_Table;
    if afe == '1' and core.Bit(ap,0) == '0':
        fault.domain     = domain;
        fault.statuscode = Fault_AccessFlag;
        return (fault, TTWState UNKNOWN);
    # Decode the TEX, C, B and S bits to produce target memory attributes
    if tre == '1':
        walkstate.memattrs = core.RemappedTEXDecode(regime, tex, c, b, s);
    elsif core.RemapRegsHaveResetValues():
        walkstate.memattrs = core.DefaultTEXDecode(tex, c, b, s);
    else:
        walkstate.memattrs = MemoryAttributes IMPLEMENTATION_DEFINED;
    walkstate.permissions.ap  = ap;
    walkstate.permissions.xn  = xn;
    walkstate.permissions.pxn = pxn;
    walkstate.domain = domain;
    walkstate.nG     = nG;
    if accdesc.ss == SS_Secure and ns == '0':
        walkstate.baseaddress.paspace = PAS_Secure;
    else:
        walkstate.baseaddress.paspace = PAS_NonSecure;
    return (fault, walkstate);
# core.SDStageOA()
# ===================
# Given the final walk state of a short-descriptor translation walk,
# map the untranslated input address bits to the base output address
FullAddress core.SDStageOA(FullAddress baseaddress, core.bits(32) va, SDFType sdftype)
    tsize = 0;
    case sdftype of
        when SDFType_SmallPage      tsize = 12;
        when SDFType_LargePage      tsize = 16;
        when SDFType_Section        tsize = 20;
        when SDFType_Supersection   tsize = 24;
    # Output Address
    FullAddress oa;
    oa.address = baseaddress.address<55:tsize>:va<tsize-1:0>;
    oa.paspace = baseaddress.paspace;
    return oa;
constant core.bits(2) Domain_NoAccess = '00';
constant core.bits(2) Domain_Client   = '01';
constant core.bits(2) Domain_Manager  = '11';
# core.S1TranslateSD()
# =======================
# Perform a stage 1 translation using short-descriptor format mapping VA to IPA/PA
# depending on the regime
(FaultRecord, AddressDescriptor, SDFType) core.S1TranslateSD(FaultRecord fault_in, Regime regime,
                                                                core.bits(32) va, boolean aligned,
                                                                AccessDescriptor accdesc)
    FaultRecord fault = fault_in;
    if not core.S1Enabled(regime, accdesc.ss):
        AddressDescriptor ipa;
        (fault, ipa) = core.S1DisabledOutput(fault, regime, va, aligned, accdesc);
        return (fault, ipa, SDFType UNKNOWN);
    TTWState walkstate;
    (fault, walkstate) = core.S1WalkSD(fault, regime, accdesc, va);
    if fault.statuscode != Fault_None:
        return (fault, AddressDescriptor UNKNOWN, SDFType UNKNOWN);
    domain = core.OutputDomain(regime, walkstate.domain);
    core.SetInGuardedPage(False);  # AArch32-VMSA does not guard any pages
    bit ntlsmd;
    if core.HaveTrapLoadStoreMultipleDeviceExt():
        case regime of
            when Regime_EL30 ntlsmd = SCTLR_S.nTLSMD;
            when Regime_EL10 ntlsmd = SCTLR_NS.nTLSMD if core.HaveAArch32EL(EL3) else SCTLR.nTLSMD;
    else:
        ntlsmd = '1';
    if core.S1HasAlignmentFault(accdesc, aligned, ntlsmd, walkstate.memattrs):
        fault.statuscode = Fault_Alignment;
    elsif (not (accdesc.acctype IN {AccessType_IC, AccessType_DC}) and
            domain == Domain_NoAccess) then
        fault.statuscode = Fault_Domain;
    elsif domain == Domain_Client:
        if core.S1SDHasPermissionsFault(regime, walkstate.permissions,
                                           walkstate.memattrs.memtype,
                                           walkstate.baseaddress.paspace,
                                           accdesc) then
            fault.statuscode = Fault_Permission;
    if fault.statuscode != Fault_None:
        fault.domain = walkstate.domain;
        return (fault, AddressDescriptor UNKNOWN, walkstate.sdftype);
    MemoryAttributes memattrs;
    if ((accdesc.acctype == AccessType_IFETCH and
            (walkstate.memattrs.memtype == MemType_Device or not core.S1ICacheEnabled(regime))) or
        (accdesc.acctype != AccessType_IFETCH and
             walkstate.memattrs.memtype == MemType_Normal and not core.S1DCacheEnabled(regime))) then
        # Treat memory attributes as Normal Non-Cacheable
        memattrs = core.NormalNCMemAttr();
        memattrs.xs = walkstate.memattrs.xs;
    else:
        memattrs = walkstate.memattrs;
    # Shareability value of stage 1 translation subject to stage 2 is IMPLEMENTATION DEFINED
    # to be either effective value or descriptor value
    if (regime == Regime_EL10 and core.EL2Enabled(accdesc.ss) and
        (HCR.VM if core.ELStateUsingAArch32(EL2, accdesc.ss==SS_Secure) else HCR_EL2.VM) == '1' and
        not (boolean IMPLEMENTATION_DEFINED "Apply effective shareability at stage 1")) then
        memattrs.shareability = walkstate.memattrs.shareability;
    else:
        memattrs.shareability = core.EffectiveShareability(memattrs);
    # Output Address
    oa = core.SDStageOA(walkstate.baseaddress, va, walkstate.sdftype);
    ipa = core.CreateAddressDescriptor(core.ZeroExtend(va, 64), oa, memattrs);
    return (fault, ipa, walkstate.sdftype);
# core.FullTranslate()
# =======================
# Perform address translation as specified by VMSA-A32
AddressDescriptor core.FullTranslate(core.bits(32) va, AccessDescriptor accdesc, boolean aligned)
    # Prepare fault fields in case a fault is detected
    FaultRecord fault = core.NoFault(accdesc);
    Regime regime = core.TranslationRegime(accdesc.el);
    # First Stage Translation
    AddressDescriptor ipa;
    if regime == Regime_EL2 or TTBCR.EAE == '1':
        (fault, ipa) = core.S1TranslateLD(fault, regime, va, aligned, accdesc);
    else:
        (fault, ipa, -) = core.S1TranslateSD(fault, regime, va, aligned, accdesc);
    if fault.statuscode != Fault_None:
        return core.CreateFaultyAddressDescriptor(core.ZeroExtend(va, 64), fault);
    if regime == Regime_EL10 and core.EL2Enabled():
        ipa.vaddress = core.ZeroExtend(va, 64);
        AddressDescriptor pa;
        (fault, pa) = core.S2Translate(fault, ipa, aligned, accdesc);
        if fault.statuscode != Fault_None:
            return core.CreateFaultyAddressDescriptor(core.ZeroExtend(va, 64), fault);
        else:
            return pa;
    else:
        return ipa;
# core.RegimeUsingAArch32()
# ====================
# Determine if the EL controlling the regime executes in AArch32 state
boolean core.RegimeUsingAArch32(Regime regime)
    case regime of
        when Regime_EL10 return core.ELUsingAArch32(EL1);
        when Regime_EL30 return True;
        when Regime_EL20 return False;
        when Regime_EL2  return core.ELUsingAArch32(EL2);
        when Regime_EL3  return False;
# core.TranslateAddress()
# ==========================
# Main entry point for translating an address
AddressDescriptor core.TranslateAddress(core.bits(32) va, AccessDescriptor accdesc,
                                           boolean aligned, integer size)
    Regime regime = core.TranslationRegime(core.APSR.EL);
    if not core.RegimeUsingAArch32(regime):
        return AArch64.core.TranslateAddress(core.ZeroExtend(va, 64), accdesc, aligned, size);
    AddressDescriptor result = core.FullTranslate(va, accdesc, aligned);
    if not core.IsFault(result):
        result.fault = core.CheckDebug(va, accdesc, size);
    # Update virtual address for abort functions
    result.vaddress = core.ZeroExtend(va, 64);
    return result;
# core.ClearExclusiveByAddress()
# =========================
# Clear the global Exclusives monitors for all PEs EXCEPT processorid if they
# record any part of the physical address region of size bytes starting at paddress.
# It is IMPLEMENTATION DEFINED whether the global Exclusives monitor for processorid
# is also cleared if it records any part of the address region.
core.ClearExclusiveByAddress(FullAddress paddress, integer processorid, integer size);
# core.HandleExternalAbort()
# =====================
# Takes a Synchronous/Asynchronous abort based on fault.
core.HandleExternalAbort(PhysMemRetStatus memretstatus, boolean iswrite,
                    AddressDescriptor memaddrdesc, integer size,
                    AccessDescriptor accdesc)
    assert (memretstatus.statuscode IN {Fault_SyncExternal, Fault_AsyncExternal} or
           (not core.HaveRASExt() and memretstatus.statuscode IN {Fault_SyncParity,
                                                         Fault_AsyncParity}));
    fault = core.NoFault(accdesc);
    fault.statuscode = memretstatus.statuscode;
    fault.write      = iswrite;
    fault.extflag    = memretstatus.extflag;
    # It is implementation specific whether External aborts signaled
    # in-band synchronously are taken synchronously or asynchronously
    if (core.IsExternalSyncAbort(fault) and
            not core.IsExternalAbortTakenSynchronously(memretstatus, iswrite, memaddrdesc,
                                               size, accdesc)) then
        if fault.statuscode == Fault_SyncParity:
            fault.statuscode = Fault_AsyncParity;
        else:
            fault.statuscode = Fault_AsyncExternal;
    if core.HaveRASExt():
        fault.merrorstate = memretstatus.merrorstate;
    if core.IsExternalSyncAbort(fault):
        if core.UsingAArch32():
            core.Abort(core.Field(memaddrdesc.vaddress,31,0), fault);
        else:
            AArch64.core.Abort(memaddrdesc.vaddress, fault);
    else:
        core.PendSErrorInterrupt(fault);
# core.HandleExternalReadAbort()
# =========================
# Wrapper function for HandleExternalAbort function in case of an External
# Abort on memory read.
core.HandleExternalReadAbort(PhysMemRetStatus memstatus, AddressDescriptor memaddrdesc,
                        integer size, AccessDescriptor accdesc)
    iswrite = False;
    core.HandleExternalAbort(memstatus, iswrite, memaddrdesc, size, accdesc);
# core.HandleExternalWriteAbort()
# ==========================
# Wrapper function for HandleExternalAbort function in case of an External
# Abort on memory write.
core.HandleExternalWriteAbort(PhysMemRetStatus memstatus, AddressDescriptor memaddrdesc,
                         integer size, AccessDescriptor accdesc)
    iswrite = True;
    core.HandleExternalAbort(memstatus, iswrite, memaddrdesc, size, accdesc);
# core.IsAligned()
# ===========
boolean core.IsAligned(integer x, integer y)
    return x == core.Align(x, y);
# core.IsAligned()
# ===========
boolean core.IsAligned(core.bits(N) x, integer y)
    return x == core.Align(x, y);
# AArch32.MemSingle[] - non-assignment (read) form
# ================================================
# Perform an atomic, little-endian read of 'size' bytes.
core.bits(size*8) AArch32.MemSingle[core.bits(32) address, integer size,
                               AccessDescriptor accdesc, boolean aligned]
    boolean ispair = False;
    return AArch32.MemSingle[address, size, accdesc, aligned, ispair];
# AArch32.MemSingle[] - non-assignment (read) form
# ================================================
# Perform an atomic, little-endian read of 'size' bytes.
core.bits(size*8) AArch32.MemSingle[core.bits(32) address, integer size, AccessDescriptor accdesc_in,
                               boolean aligned, boolean ispair]
    assert size IN {1, 2, 4, 8, 16};
    core.bits(size*8) value;
    AccessDescriptor accdesc = accdesc_in;
    assert core.IsAligned(address, size);
    AddressDescriptor memaddrdesc;
    memaddrdesc = core.TranslateAddress(address, accdesc, aligned, size);
    # Check for aborts or debug exceptions
    if core.IsFault(memaddrdesc):
        core.Abort(address, memaddrdesc.fault);
    # Memory array access
    if SPESampleInFlight:
        boolean is_load = True;
        core.SPESampleLoadStore(is_load, accdesc, memaddrdesc);
    PhysMemRetStatus memstatus;
    (memstatus, value) = core.PhysMemRead(memaddrdesc, size, accdesc);
    if core.IsFault(memstatus):
        core.HandleExternalReadAbort(memstatus, memaddrdesc, size, accdesc);
    return value;
# AArch32.MemSingle[] - assignment (write) form
# =============================================
AArch32.MemSingle[core.bits(32) address, integer size,
                  AccessDescriptor accdesc, boolean aligned] = core.bits(size*8) value
    boolean ispair = False;
    AArch32.MemSingle[address, size, accdesc, aligned, ispair] = value;
    return;
# AArch32.MemSingle[] - assignment (write) form
# =============================================
# Perform an atomic, little-endian write of 'size' bytes.
AArch32.MemSingle[core.bits(32) address, integer size, AccessDescriptor accdesc_in,
                  boolean aligned, boolean ispair] = core.bits(size*8) value
    assert size IN {1, 2, 4, 8, 16};
    AccessDescriptor accdesc = accdesc_in;
    assert core.IsAligned(address, size);
    AddressDescriptor memaddrdesc;
    memaddrdesc = core.TranslateAddress(address, accdesc, aligned, size);
    # Check for aborts or debug exceptions
    if core.IsFault(memaddrdesc):
        core.Abort(address, memaddrdesc.fault);
    # Effect on exclusives
    if memaddrdesc.memattrs.shareability != Shareability_NSH:
        core.ClearExclusiveByAddress(memaddrdesc.paddress, core.ProcessorID(), size);
    if SPESampleInFlight:
        boolean is_load = False;
        core.SPESampleLoadStore(is_load, accdesc, memaddrdesc);
    PhysMemRetStatus memstatus;
    memstatus = core.PhysMemWrite(memaddrdesc, size, accdesc, value);
    if core.IsFault(memstatus):
        core.HandleExternalWriteAbort(memstatus, memaddrdesc, size, accdesc);
    return;
# core.CreateAccDescIFetch()
# =====================
# Access descriptor for instruction fetches
AccessDescriptor core.CreateAccDescIFetch()
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_IFETCH);
    return accdesc;
# core.CheckITEnabled()
# ========================
# Check whether the T32 IT instruction is disabled.
core.CheckITEnabled(core.bits(4) mask)
    bit it_disabled;
    if core.APSR.EL == EL2:
        it_disabled = HSCTLR.ITD;
    else:
        it_disabled = (SCTLR.ITD if core.ELUsingAArch32(EL1) else SCTLR[].ITD);
    if it_disabled == '1':
        if mask != '1000': raise Exception('UNDEFINED');
        accdesc = core.CreateAccDescIFetch();
        aligned = True;
        # Otherwise whether the IT block is allowed depends on hw1 of the next instruction.
        next_instr = AArch32.MemSingle[core.NextInstrAddr(32), 2, accdesc, aligned];
        if next_instr IN {'11xxxxxxxxxxxxxx', '1011xxxxxxxxxxxx', '10100xxxxxxxxxxx',
                          '01001xxxxxxxxxxx', '010001xxx1111xxx', '010001xx1xxxx111'} then
            # It is IMPLEMENTATION DEFINED whether the Undefined Instruction exception is
            # taken on the IT instruction or the next instruction. This is not reflected in
            # the pseudocode, which always takes the exception on the IT instruction. This
            # also does not take into account cases where the next instruction is raise Exception('UNPREDICTABLE').
            raise Exception('UNDEFINED');
    return;
# core.IsExclusiveVA()
# =======================
# An optional IMPLEMENTATION DEFINED test for an exclusive access to a virtual
# address region of size bytes starting at address.
#
# It is permitted (but not required) for this function to return False and
# cause a store exclusive to fail if the virtual address region is not
# totally included within the region recorded by core.MarkExclusiveVA().
#
# It is always safe to return True which will check the physical address only.
boolean core.IsExclusiveVA(core.bits(32) address, integer processorid, integer size);
# core.AlignmentFault()
# ================
# Return a fault record indicating an Alignment fault not due to memory type1 has occured
# for a specific access
FaultRecord core.AlignmentFault(AccessDescriptor accdesc)
    FaultRecord fault;
    fault.statuscode  = Fault_Alignment;
    fault.access      = accdesc;
    fault.secondstage = False;
    fault.s2fs1walk   = False;
    fault.write       = not accdesc.read and accdesc.write;
    fault.gpcfs2walk  = False;
    fault.gpcf        = core.GPCNoFault();
    return fault;
# MemOp
# =====
# Memory access instruction types.
enumeration MemOp {MemOp_LOAD, MemOp_STORE, MemOp_PREFETCH};
# core.CreateAccDescExLDST()
# =====================
# Access descriptor for general purpose register loads/stores with exclusive semantics
AccessDescriptor core.CreateAccDescExLDST(MemOp memop, boolean acqrel, boolean tagchecked)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_GPR);
    accdesc.acqsc           = acqrel and memop == MemOp_LOAD;
    accdesc.relsc           = acqrel and memop == MemOp_STORE;
    accdesc.exclusive       = True;
    accdesc.read            = memop == MemOp_LOAD;
    accdesc.write           = memop == MemOp_STORE;
    accdesc.pan             = True;
    accdesc.tagchecked      = tagchecked;
    accdesc.transactional   = core.HaveTME() and TSTATE.depth > 0;
    return accdesc;
# core.IsExclusiveGlobal()
# ===================
# Return True if the global Exclusives monitor for processorid includes all of
# the physical address region of size bytes starting at paddress.
boolean core.IsExclusiveGlobal(FullAddress paddress, integer processorid, integer size);
# core.IsExclusiveLocal()
# ==================
# Return True if the local Exclusives monitor for processorid includes all of
# the physical address region of size bytes starting at paddress.
boolean core.IsExclusiveLocal(FullAddress paddress, integer processorid, integer size);
# core.ExclusiveMonitorsPass()
# ===============================
# Return True if the Exclusives monitors for the current PE include all of the addresses
# associated with the virtual address region of size bytes starting at address.
# The immediately following memory write must be to the same addresses.
boolean core.ExclusiveMonitorsPass(core.bits(32) address, integer size)
    # It is IMPLEMENTATION DEFINED whether the detection of memory aborts happens
    # before or after the check on the local Exclusives monitor. As a result a failure
    # of the local monitor can occur on some implementations even if the memory
    # access would give an memory abort.
    boolean acqrel = False;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescExLDST(MemOp_STORE, acqrel, tagchecked);
    boolean aligned = core.IsAligned(address, size);
    if not aligned:
        core.Abort(address, core.AlignmentFault(accdesc));
    if not core.IsExclusiveVA(address, core.ProcessorID(), size):
        return False;
    memaddrdesc = core.TranslateAddress(address, accdesc, aligned, size);
    # Check for aborts or debug exceptions
    if core.IsFault(memaddrdesc):
        core.Abort(address, memaddrdesc.fault);
    passed = core.IsExclusiveLocal(memaddrdesc.paddress, core.ProcessorID(), size);
    core.ClearExclusiveLocal(core.ProcessorID());
    if passed and memaddrdesc.memattrs.shareability != Shareability_NSH:
        passed = core.IsExclusiveGlobal(memaddrdesc.paddress, core.ProcessorID(), size);
    return passed;
# core.MarkExclusiveVA()
# =========================
# Optionally record an exclusive access to the virtual address region of size bytes
# starting at address for processorid.
core.MarkExclusiveVA(core.bits(32) address, integer processorid, integer size);
# core.MarkExclusiveGlobal()
# =====================
# Record the physical address region of size bytes starting at paddress in
# the global Exclusives monitor for processorid.
core.MarkExclusiveGlobal(FullAddress paddress, integer processorid, integer size);
# core.MarkExclusiveLocal()
# ====================
# Record the physical address region of size bytes starting at paddress in
# the local Exclusives monitor for processorid.
core.MarkExclusiveLocal(FullAddress paddress, integer processorid, integer size);
# core.SetExclusiveMonitors()
# ==============================
# Sets the Exclusives monitors for the current PE to record the addresses associated
# with the virtual address region of size bytes starting at address.
core.SetExclusiveMonitors(core.bits(32) address, integer size)
    boolean acqrel = False;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescExLDST(MemOp_LOAD, acqrel, tagchecked);
    boolean aligned = core.IsAligned(address, size);
    if not aligned:
        core.Abort(address, core.AlignmentFault(accdesc));
    memaddrdesc = core.TranslateAddress(address, accdesc, aligned, size);
    # Check for aborts or debug exceptions
    if core.IsFault(memaddrdesc):
        return;
    if memaddrdesc.memattrs.shareability != Shareability_NSH:
        core.MarkExclusiveGlobal(memaddrdesc.paddress, core.ProcessorID(), size);
    core.MarkExclusiveLocal(memaddrdesc.paddress, core.ProcessorID(), size);
    core.MarkExclusiveVA(address, core.ProcessorID(), size);
# AArch64.core.SoftwareBreakpoint()
# ============================
AArch64.core.SoftwareBreakpoint(core.bits(16) immediate)
    route_to_el2 = (core.APSR.EL IN {EL0, EL1} and
                    core.EL2Enabled() and (HCR_EL2.TGE == '1' or MDCR_EL2.TDE == '1'));
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    vect_offset = 0x0;
    exception = core.ExceptionSyndrome(Exception_SoftwareBreakpoint);
    exception.syndrome = core.SetField(exception.syndrome,15,0,immediate);
    if core.UInt(core.APSR.EL) > core.UInt(EL1):
        AArch64.core.TakeException(core.APSR.EL, exception, preferred_exception_return, vect_offset);
    elsif route_to_el2:
        AArch64.core.TakeException(EL2, exception, preferred_exception_return, vect_offset);
    else:
        AArch64.core.TakeException(EL1, exception, preferred_exception_return, vect_offset);
# core.SoftwareBreakpoint()
# ============================
core.SoftwareBreakpoint(core.bits(16) immediate)
    if (core.EL2Enabled() and not core.ELUsingAArch32(EL2) and
        (HCR_EL2.TGE == '1' or MDCR_EL2.TDE == '1')) or not core.ELUsingAArch32(EL1) then
        AArch64.core.SoftwareBreakpoint(immediate);
    accdesc  = core.CreateAccDescIFetch();
    fault    = core.NoFault(accdesc);
    vaddress = UNKNOWN = 0;
    fault.statuscode = Fault_Debug;
    fault.debugmoe   = DebugException_BKPT;
    core.Abort(vaddress, fault);
# AArch64.core.MonitorModeTrap()
# =========================
# Trapped use of Monitor mode features in a Secure EL1 AArch32 mode
AArch64.core.MonitorModeTrap()
    core.bits(64) preferred_exception_return = core.ThisInstrAddr(64);
    vect_offset = 0x0;
    exception = core.ExceptionSyndrome(Exception_Uncategorized);
    if core.IsSecureEL2Enabled():
        AArch64.core.TakeException(EL2, exception, preferred_exception_return, vect_offset);
    AArch64.core.TakeException(EL3, exception, preferred_exception_return, vect_offset);
EventRegister = 0;
# core.SendEventLocal()
# ================
# Set the local Event Register of this PE.
# When a PE executes the SEVL instruction, it causes this function to be executed.
core.SendEventLocal()
    EventRegister = '1';
    return;
# core.ELFromSPSR()
# ============
# Convert an SPSR value encoding to an Exception level.
# Returns (valid,EL):
#   'valid' is True if 'core.Field(spsr,4,0)' encodes a valid mode for the current state.
#   'EL'    is the Exception level decoded from 'spsr'.
(boolean,core.bits(2)) core.ELFromSPSR(core.bits(N) spsr)
    el = 0;
    valid = False;
    effective_nse_ns = 0;
    if core.Bit(spsr,4) == '0':
              # AArch64 state
        el = core.Field(spsr,3,2);
        effective_nse_ns = core.EffectiveSCR_EL3_NSE() : core.EffectiveSCR_EL3_NS();
        if not core.HaveAArch64():
            valid = False;      # No AArch64 support
        elsif not core.HaveEL(el):
            valid = False;      # Exception level not implemented
        elsif core.Bit(spsr,1) == '1':
            valid = False;      # M[1] must be 0
        elsif el == EL0 and core.Bit(spsr,0) == '1':
            valid = False;      # for EL0, M[0] must be 0
        elsif core.HaveRME() and el != EL3 and effective_nse_ns == '10':
            valid = False;      # Only EL3 valid in Root state
        elsif el == EL2 and core.HaveEL(EL3) and not core.IsSecureEL2Enabled() and SCR_EL3.NS == '0':
            valid = False;      # Unless Secure EL2 is enabled, EL2 valid only in Non-secure state
        else:
            valid = True;
    elsif core.HaveAArch32():
        # AArch32 state
        (valid, el) = core.ELFromM32(core.Field(spsr,4,0));
    else:
        valid = False;
    if not valid:
         el = UNKNOWN = 0;
    return (valid,el);
# core.ELUsingAArch32K()
# =================
(boolean,boolean) core.ELUsingAArch32K(core.bits(2) el)
    return core.ELStateUsingAArch32K(el, core.IsSecureBelowEL3());
# core.IllegalExceptionReturn()
# ========================
boolean core.IllegalExceptionReturn(core.bits(N) spsr)
    # Check for illegal return:
    #   * To an unimplemented Exception level.
    #   * To EL2 in Secure state, when SecureEL2 is not enabled.
    #   * To EL0 using AArch64 state, with SPSR.M[0]==1.
    #   * To AArch64 state with SPSR.M[1]==1.
    #   * To AArch32 state with an illegal value of SPSR.M.
    (valid, target) = core.ELFromSPSR(spsr);
    if not valid:
         return True;
    # Check for return to higher Exception level
    if core.UInt(target) > core.UInt(core.APSR.EL):
         return True;
    spsr_mode_is_aarch32 = (core.Bit(spsr,4) == '1');
    # Check for illegal return:
    #   * To EL1, EL2 or EL3 with register width specified in the SPSR different from the
    #     Execution state used in the Exception level being returned to, as determined by
    #     the SCR_EL3.RW or HCR_EL2.RW bits, or as configured from reset.
    #   * To EL0 using AArch64 state when EL1 is using AArch32 state as determined by the
    #     SCR_EL3.RW or HCR_EL2.RW bits or as configured from reset.
    #   * To AArch64 state from AArch32 state (should be caught by above)
    (known, target_el_is_aarch32) = core.ELUsingAArch32K(target);
    assert known or (target == EL0 and not core.ELUsingAArch32(EL1));
    if known and spsr_mode_is_aarch32 != target_el_is_aarch32:
         return True;
    # Check for illegal return from AArch32 to AArch64
    if core.UsingAArch32() and not spsr_mode_is_aarch32:
         return True;
    # Check for illegal return to EL1 when HCR.TGE is set and when either of
    # * SecureEL2 is enabled.
    # * SecureEL2 is not enabled and EL1 is in Non-secure state.
    if core.HaveEL(EL2) and target == EL1 and HCR_EL2.TGE == '1':
        if (not core.IsSecureBelowEL3() or core.IsSecureEL2Enabled()): return True;
    if (core.HaveGCS() and core.APSR.EXLOCK == '0' and core.APSR.EL == target and
        core.GetCurrentEXLOCKEN() and not core.Halted()) then
        return True;
    return False;
# core.Restarting()
# ============
boolean core.Restarting()
    return EDSCR.STATUS == '000001';                                    # Restarting
# core.DebugExceptionReturnSS()
# ========================
# Returns value to write to core.APSR.SS on an exception return or Debug state exit.
bit core.DebugExceptionReturnSS(core.bits(N) spsr)
    assert core.Halted() or core.Restarting() or  core.APSR.EL != EL0;
    enabled_at_source = False;
    if core.Restarting():
        enabled_at_source = False;
    elsif core.UsingAArch32():
        enabled_at_source = core.GenerateDebugExceptions();
    else:
        enabled_at_source = AArch64.core.GenerateDebugExceptions();
    valid = False;
    dest_el = 0;
    if core.IllegalExceptionReturn(spsr):
        dest_el = core.APSR.EL;
    else:
        (valid, dest_el) = core.ELFromSPSR(spsr);  assert valid;
    dest_ss = core.SecurityStateAtEL(dest_el);
    bit mask;
    enabled_at_dest = False;
    dest_using_32 = (core.Bit(spsr,4) == '1' if dest_el == EL0 else core.ELUsingAArch32(dest_el));
    if dest_using_32:
        enabled_at_dest = core.GenerateDebugExceptionsFrom(dest_el, dest_ss);
    else:
        mask = core.Bit(spsr,9);
        enabled_at_dest = AArch64.core.GenerateDebugExceptionsFrom(dest_el, dest_ss, mask);
    ELd = core.DebugTargetFrom(dest_ss);
    bit SS_bit;
    if not core.ELUsingAArch32(ELd) and MDSCR_EL1.SS == '1' and not enabled_at_source and enabled_at_dest:
        SS_bit = core.Bit(spsr,21);
    else:
        SS_bit = '0';
    return SS_bit;
# core.RestoredITBits()
# ================
# Get the value of core.APSR.IT to be restored on this exception return.
core.bits(8) core.RestoredITBits(core.bits(N) spsr)
    it = spsr<15:10,26:25>;
    # When core.APSR.IL is set, it is CONSTRAINED raise Exception('UNPREDICTABLE') whether the IT bits are each set
    # to zero or copied from the SPSR.
    if core.APSR.IL == '1':
        if core.ConstrainUnpredictableBool(Unpredictable_ILZEROIT): return '00000000';
        else return it;
    # The IT bits are forced to zero when they are set to a reserved value.
    if not core.IsZero(core.Field(it,7,4)) and core.IsZero(core.Field(it,3,0)):
        return '00000000';
    # The IT bits are forced to zero when returning to A32 state, or when returning to an EL
    # with the ITD bit set to 1, and the IT bits are describing a multi-instruction block.
    itd = HSCTLR.ITD if core.APSR.EL == EL2 else SCTLR.ITD;
    if (core.Bit(spsr,5) == '0' and not core.IsZero(it)) or (itd == '1' and not core.IsZero(core.Field(it,2,0))):
        return '00000000';
    else:
        return it;
ShouldAdvanceIT = False;
ShouldAdvanceSS = False;
# core.Setcore.APSRFromPSR()
# ==================
core.Setcore.APSRFromPSR(core.bits(N) spsr)
    boolean illegal_psr_state = core.IllegalExceptionReturn(spsr);
    core.Setcore.APSRFromPSR(spsr, illegal_psr_state);
# core.Setcore.APSRFromPSR()
# ==================
# Set core.APSR based on a PSR value
core.Setcore.APSRFromPSR(core.bits(N) spsr_in, boolean illegal_psr_state)
    core.bits(N) spsr = spsr_in;
    boolean from_aarch64 = not core.UsingAArch32();
    core.APSR.SS = core.DebugExceptionReturnSS(spsr);
    ShouldAdvanceSS = False;
    if illegal_psr_state:
        core.APSR.IL = '1';
        if core.HaveSSBSExt():
             core.APSR.SSBS = bit UNKNOWN;
        if core.HaveBTIExt():
             core.APSR.BTYPE = UNKNOWN = 0;
        if core.HaveUAOExt():
             core.APSR.UAO = bit UNKNOWN;
        if core.HaveDITExt():
             core.APSR.DIT = bit UNKNOWN;
        if core.HaveMTEExt():
             core.APSR.TCO = bit UNKNOWN;
    else:
        # State that is reinstated only on a legal exception return
        core.APSR.IL = core.Bit(spsr,20);
        if core.Bit(spsr,4) == '1':
                                # AArch32 state
            core.WriteMode(core.Field(spsr,4,0));         # Sets core.APSR.EL correctly
            if core.HaveSSBSExt():
                 core.APSR.SSBS = core.Bit(spsr,23);
        else                                      # AArch64 state
            core.APSR.nRW = '0';
            core.APSR.EL  = core.Field(spsr,3,2);
            core.APSR.SP  = core.Bit(spsr,0);
            if core.HaveBTIExt():
                 core.APSR.BTYPE = core.Field(spsr,11,10);
            if core.HaveSSBSExt():
                 core.APSR.SSBS = core.Bit(spsr,12);
            if core.HaveUAOExt():
                 core.APSR.UAO = core.Bit(spsr,23);
            if core.HaveDITExt():
                 core.APSR.DIT = core.Bit(spsr,24);
            if core.HaveMTEExt():
                 core.APSR.TCO = core.Bit(spsr,25);
            if core.HaveGCS():
                 core.APSR.EXLOCK = core.Bit(spsr,34);
    # If core.APSR.IL is set, it is CONSTRAINED raise Exception('UNPREDICTABLE') whether the T bit is set to zero or
    # copied from SPSR.
    if core.APSR.IL == '1' and core.APSR.nRW == '1':
        if core.ConstrainUnpredictableBool(Unpredictable_ILZEROT): spsr = core.SetBit(spsr,5,'0')
    # State that is reinstated regardless of illegal exception return
    core.APSR.<N,Z,C,V> = core.Field(spsr,31,28);
    if core.HavePANExt():
         core.APSR.PAN = core.Bit(spsr,22);
    if core.APSR.nRW == '1':
                             # AArch32 state
        core.APSR.Q         = core.Bit(spsr,27);
        core.APSR.IT        = core.RestoredITBits(spsr);
        ShouldAdvanceIT  = False;
        if core.HaveDITExt():
            core.APSR.DIT = (core.Bit(spsr,24) if (core.Restarting() or from_aarch64) else core.Bit(spsr,21));
        core.APSR.GE        = core.Field(spsr,19,16);
        core.APSR.E         = core.Bit(spsr,9);
        core.APSR.<A,I,F>   = core.Field(spsr,8,6);             # No core.APSR.D in AArch32 state
        core.APSR.T         = core.Bit(spsr,5);               # core.APSR.J is RES0
    else                                          # AArch64 state
        if core.HaveFeatNMI():
             core.APSR.ALLINT = core.Bit(spsr,13);
        core.APSR.<D,A,I,F> = core.Field(spsr,9,6);             # No core.APSR.<Q,IT,GE,E,T> in AArch64 state
    return;
# core.ExceptionReturn()
# =========================
core.ExceptionReturn(core.bits(32) new_pc_in, core.bits(32) spsr)
    core.bits(32) new_pc = new_pc_in;
    core.SynchronizeContext();
    # Attempts to change to an illegal mode or state will invoke the Illegal Execution state
    # mechanism
    core.Setcore.APSRFromPSR(spsr);
    core.ClearExclusiveLocal(core.ProcessorID());
    core.SendEventLocal();
    if core.APSR.IL == '1':
        # If the exception return is illegal, PC[1:0] are UNKNOWN
        new_pc = core.SetField(new_pc,1,0,UNKNOWN = 0);
    else:
        # Lcore.R[1:0] or Lcore.readR(0) are treated as being 0, depending on the target instruction set state
        if core.APSR.T == '1':
            new_pc = core.SetBit(new_pc,0,'0')                 # T32
        else:
            new_pc = core.SetField(new_pc,1,0,'00');              # A32
    boolean branch_conditional = not (core.CurrentCond() IN {'111x'});
    core.BranchTo(new_pc, 'ERET', branch_conditional);
    core.CheckExceptionCatch(False);              # Check for debug event on exception return
# core.ALUExceptionReturn()
# ====================
core.ALUExceptionReturn(core.bits(32) address)
    if core.APSR.EL == EL2:
        raise Exception('UNDEFINED');
    elsif core.APSR.M IN {M32_User,M32_System}:
        Constraint c = core.ConstrainUnpredictable(Unpredictable_ALUEXCEPTIONRETURN);
        assert c IN {Constraint_UNDEF, Constraint_NOP};
        case c of
            when Constraint_UNDEF
                raise Exception('UNDEFINED');
            when Constraint_NOP
                core.EndOfInstruction();
    else:
        core.ExceptionReturn(address, SPSR[]);
# core.SelectInstrSet()
# ================
core.SelectInstrSet(InstrSet iset)
    assert core.CurrentInstrSet() IN {InstrSet_A32, InstrSet_T32};
    assert iset IN {InstrSet_A32, InstrSet_T32};
    core.APSR.T = '0' if iset == InstrSet_A32 else '1';
    return;
# core.BXWritePC()
# ===========
core.BXWritePC(core.bits(32) address_in, BranchType branch_type)
    core.bits(32) address = address_in;
    if core.Bit(address,0) == '1':
        core.SelectInstrSet(InstrSet_T32);
        address = core.SetBit(address,0,'0')
    else:
        core.SelectInstrSet(InstrSet_A32);
        # For branches to an unaligned PC counter in A32 state, the processor takes the branch
        # and does one of:
        # * Forces the address to be aligned
        # * Leaves the PC unaligned, meaning the target generates a PC Alignment fault.
        if core.Bit(address,1) == '1' and core.ConstrainUnpredictableBool(Unpredictable_A32FORCEALIGNPC):
            address = core.SetBit(address,1,'0')
    boolean branch_conditional = not (core.CurrentCond() IN {'111x'});
    core.BranchTo(address, branch_type, branch_conditional);
# core.BranchWritePC()
# ===============
core.BranchWritePC(core.bits(32) address_in, BranchType branch_type)
    core.bits(32) address = address_in;
    if True:
        address = core.SetBit(address,0,'0')
    boolean branch_conditional = not (core.CurrentCond() IN {'111x'});
    core.BranchTo(address, branch_type, branch_conditional);
# core.ALUWritePC()
# ============
core.ALUWritePC(core.bits(32) address)
    if True:
        core.BranchWritePC(address, 'INDIR');
# core.Abs()
# =====
integer core.Abs(integer x)
    return x if x >= 0 else -x;
# core.Abs()
# =====
real core.Abs(real x)
    return x if x >= 0.0 else -x;
# core.SInt()
# ======
integer core.SInt(core.bits(N) x)
    result = 0;
    for i = 0 to N-1
        if x<i> == '1':
             result = result + 2^i;
    if x<N-1> == '1':
         result = result - 2^N;
    return result;
# core.AddWithCarry()
# ==============
# Integer addition with carry input, returning result and NZCV flags
(core.bits(N), core.bits(4)) core.AddWithCarry(core.bits(N) x, core.bits(N) y, bit carry_in)
    integer unsigned_sum = core.UInt(x) + core.UInt(y) + core.UInt(carry_in);
    integer signed_sum = core.SInt(x) + core.SInt(y) + core.UInt(carry_in);
    core.bits(N) result = unsigned_sum<N-1:0>; # same value as signed_sum<N-1:0>
    bit n = result<N-1>;
    bit z = '1' if core.IsZero(result) else '0';
    bit c = '0' if core.UInt(result) == unsigned_sum else '1';
    bit v = '0' if core.SInt(result) == signed_sum else '1';
    return (result, n:z:c:v);
# core.BankedRegisterAccessValid()
# ===========================
# Checks for MRS (Banked register) or MSR (Banked register) accesses to registers
# other than the SPSRs that are invalid. This includes ELR_hyp accesses.
core.BankedRegisterAccessValid(core.bits(5) SYSm, core.bits(5) mode)
    case SYSm of
        when '000xx', '00100'                          # R8_usr to R12_usr
            if mode != M32_FIQ:
                 raise Exception('UNPREDICTABLE');
        when '00101'                                   # SP_usr
            if mode == M32_System:
                 raise Exception('UNPREDICTABLE');
        when '00110'                                   # LR_usr
            if mode IN {M32_Hyp,M32_System}:
                 raise Exception('UNPREDICTABLE');
        when '010xx', '0110x', '01110'                 # R8_fiq to R12_fiq, SP_fiq, LR_fiq
            if mode == M32_FIQ:
                 raise Exception('UNPREDICTABLE');
        when '1000x'                                   # LR_irq, SP_irq
            if mode == M32_IRQ:
                 raise Exception('UNPREDICTABLE');
        when '1001x'                                   # LR_svc, SP_svc
            if mode == M32_Svc:
                 raise Exception('UNPREDICTABLE');
        when '1010x'                                   # LR_abt, SP_abt
            if mode == M32_Abort:
                 raise Exception('UNPREDICTABLE');
        when '1011x'                                   # LR_und, SP_und
            if mode == M32_Undef:
                 raise Exception('UNPREDICTABLE');
        when '1110x'                                   # LR_mon, SP_mon
            if (not core.HaveEL(EL3) or core.CurrentSecurityState() != SS_Secure or
                mode == M32_Monitor) then raise Exception('UNPREDICTABLE');
        when '11110'                                   # ELR_hyp, only from Monitor or Hyp mode
            if not core.HaveEL(EL2) or not (mode IN {M32_Monitor,M32_Hyp}):
                 raise Exception('UNPREDICTABLE');
        when '11111'                                   # SP_hyp, only from Monitor mode
            if not core.HaveEL(EL2) or mode != M32_Monitor:
                 raise Exception('UNPREDICTABLE');
        otherwise
            raise Exception('UNPREDICTABLE');
    return;
# core.BigEndian()
# ===========
boolean core.BigEndian(AccessType acctype)
    bigend = False;
    if core.HaveNV2Ext() and acctype == AccessType_NV2:
        return SCTLR_EL2.EE == '1';
    if core.UsingAArch32():
        bigend = (core.APSR.E != '0');
    elsif core.APSR.EL == EL0:
        bigend = (SCTLR[].E0E != '0');
    else:
        bigend = (SCTLR[].EE != '0');
    return bigend;
# core.BitCount()
# ==========
integer core.BitCount(core.bits(N) x)
    integer result = 0;
    for i = 0 to N-1
        if x<i> == '1':
            result = result + 1;
    return result;
# core.CBWritePC()
# ===========
# Takes a branch from a CBNZ/CBZ instruction.
core.CBWritePC(core.bits(32) address_in)
    core.bits(32) address = address_in;
    assert core.CurrentInstrSet() == InstrSet_T32;
    address = core.SetBit(address,0,'0')
    boolean branch_conditional = True;
    core.BranchTo(address, 'DIR', branch_conditional);
# core.WriteModeByInstr()
# ==========================
# Function for dealing with writes to core.APSR.M from an AArch32 instruction, and ensuring that
# illegal state changes are correctly flagged in core.APSR.IL.
core.WriteModeByInstr(core.bits(5) mode)
    (valid,el) = core.ELFromM32(mode);
    # 'valid' is set to False if' mode' is invalid for this implementation or the current value
    # of SCR.NS/SCR_EL3.NS. Additionally, it is illegal for an instruction to write 'mode' to
    # core.APSR.EL if it would result in any of:
    # * A change to a mode that would cause entry to a higher Exception level.
    if core.UInt(el) > core.UInt(core.APSR.EL):
        valid = False;
    # * A change to or from Hyp mode.
    if (core.APSR.M == M32_Hyp or mode == M32_Hyp) and core.APSR.M != mode:
        valid = False;
    # * When EL2 is implemented, the value of HCR.TGE is '1', a change to a Non-secure EL1 mode.
    if core.APSR.M == M32_Monitor and core.HaveEL(EL2) and el == EL1 and SCR.NS == '1' and HCR.TGE == '1':
        valid = False;
    if not valid:
        core.APSR.IL = '1';
    else:
        core.WriteMode(mode);
# core.CPSRWriteByInstr()
# ==================
# Update core.APSR.<N,Z,C,V,Q,GE,E,A,I,F,M> from a CPSR value written by an MSR instruction.
core.CPSRWriteByInstr(core.bits(32) value, core.bits(4) bytemask)
    privileged = core.APSR.EL != EL0;              # core.APSR.<A,I,F,M> are not writable at EL0
    # Write core.APSR from 'value', ignoring bytes masked by 'bytemask'
    if core.Bit(bytemask,3) == '1':
        core.APSR.<N,Z,C,V,Q> = core.Field(value,31,27);
        # Bits <26:24> are ignored
    if core.Bit(bytemask,2) == '1':
        if core.HaveSSBSExt():
            core.APSR.SSBS = core.Bit(value,23);
        if privileged:
            core.APSR.PAN = core.Bit(value,22);
        if core.HaveDITExt():
            core.APSR.DIT = core.Bit(value,21);
        # Bit <20> is RES0
        core.APSR.GE = core.Field(value,19,16);
    if core.Bit(bytemask,1) == '1':
        # Bits <15:10> are RES0
        core.APSR.E = core.Bit(value,9);                    # core.APSR.E is writable at EL0
        if privileged:
            core.APSR.A = core.Bit(value,8);
    if core.Bit(bytemask,0) == '1':
        if privileged:
            core.APSR.<I,F> = core.Field(value,7,6);
            # Bit <5> is RES0
            # core.WriteModeByInstr() sets core.APSR.IL to 1 if this is an illegal mode change.
            core.WriteModeByInstr(core.Field(value,4,0));
    return;
# core.ConditionHolds()
# ================
# Return True iff COND currently holds
boolean core.ConditionHolds(core.bits(4) cond)
    # Evaluate base condition.
    result = False;
    case core.Field(cond,3,1) of
        when '000' result = (core.APSR.Z == '1');                          # EQ or NE
        when '001' result = (core.APSR.C == '1');                          # CS or CC
        when '010' result = (core.APSR.N == '1');                          # MI or PL
        when '011' result = (core.APSR.V == '1');                          # VS or VC
        when '100' result = (core.APSR.C == '1' and core.APSR.Z == '0');       # HI or LS
        when '101' result = (core.APSR.N == core.APSR.V);                     # GE or LT
        when '110' result = (core.APSR.N == core.APSR.V and core.APSR.Z == '0');  # GT or LE
        when '111' result = True;                                       # AL
    # Condition flag values in the set '111x' indicate always true
    # Otherwise, invert condition if necessary.
    if core.Bit(cond,0) == '1' and cond != '1111':
        result = not result;
    return result;
# core.ConditionPassed()
# =================
boolean core.ConditionPassed()
    return core.ConditionHolds(core.CurrentCond());
# core.HighestSetBit()
# ===============
integer core.HighestSetBit(core.bits(N) x)
    for i = N-1 downto 0
        if x<i> == '1':
             return i;
    return -1;
# core.CountLeadingZeroBits()
# ======================
integer core.CountLeadingZeroBits(core.bits(N) x)
    return N - (core.HighestSetBit(x) + 1);
# SRType
# ======
enumeration SRType {'LSL', 'LSR', 'ASR', 'ROR', 'RRX'};
# core.DecodeImmShift()
# ================
(SRType, integer) core.DecodeImmShift(core.bits(2) srtype, core.bits(5) imm5)
    SRType shift_t;
    shift_n = 0;
    case srtype of
        when '00'
            shift_t = 'LSL';  shift_n = core.UInt(imm5);
        when '01'
            shift_t = 'LSR';  shift_n = 32 if imm5 == '00000' else core.UInt(imm5);
        when '10'
            shift_t = 'ASR';  shift_n = 32 if imm5 == '00000' else core.UInt(imm5);
        when '11'
            if imm5 == '00000':
                shift_t = 'RRX';  shift_n = 1;
            else:
                shift_t = 'ROR';  shift_n = core.UInt(imm5);
    return (shift_t, shift_n);
# core.DecodeRegShift()
# ================
SRType core.DecodeRegShift(core.bits(2) srtype)
    SRType shift_t;
    case srtype of
        when '00'  shift_t = 'LSL';
        when '01'  shift_t = 'LSR';
        when '10'  shift_t = 'ASR';
        when '11'  shift_t = 'ROR';
    return shift_t;
# core.InITBlock()
# ===========
boolean core.InITBlock()
    if core.CurrentInstrSet() == InstrSet_T32:
        return core.Field(core.APSR.IT,3,0) != '0000';
    else:
        return False;
# core.IsZeroBit()
# ===========
bit core.IsZeroBit(core.bits(N) x)
    return '1' if core.IsZero(x) else '0';
# LR - assignment form
# ====================
LR = core.bits(32) value
    core.R[14] = value; log.info(f'Setting R{14}={hex(core.UInt(core.Field(value)))}')
    return;
# LR - non-assignment form
# ========================
core.bits(32) LR
    return core.readR(14);
# core.LastInITBlock()
# ===============
boolean core.LastInITBlock()
    return (core.Field(core.APSR.IT,3,0) == '1000');
# core.LoadWritePC()
# =============
core.LoadWritePC(core.bits(32) address)
    core.BXWritePC(address, 'INDIR');
# core.LowestSetBit()
# ==============
integer core.LowestSetBit(core.bits(N) x)
    for i = 0 to N-1
        if x<i> == '1':
             return i;
    return N;
# core.AlignmentEnforced()
# ===================
# For the active translation regime, determine if alignment is required by all accesses
boolean core.AlignmentEnforced()
    Regime regime = core.TranslationRegime(core.APSR.EL);
    bit A;
    case regime of
        when Regime_EL3  A = SCTLR_EL3.A;
        when Regime_EL30 A = SCTLR.A;
        when Regime_EL2  A = HSCTLR.A if core.ELUsingAArch32(EL2) else SCTLR_EL2.A;
        when Regime_EL20 A = SCTLR_EL2.A;
        when Regime_EL10 A = SCTLR.A  if core.ELUsingAArch32(EL1) else SCTLR_EL1.A;
        otherwise core.Unreachable();
    return A == '1';
# core.UnalignedAccessFaults()
# ===============================
# Determine whether the unaligned access generates an Alignment fault
boolean core.UnalignedAccessFaults(AccessDescriptor accdesc)
    return (core.AlignmentEnforced() or
            accdesc.a32lsmd     or
            accdesc.exclusive   or
            accdesc.acqsc       or
            accdesc.relsc);
# Mem_with_type[] - non-assignment (read) form
# ============================================
# Perform a read of 'size' bytes. The access byte order is reversed for a big-endian access.
# Instruction fetches would call AArch32.MemSingle directly.
core.bits(size*8) Mem_with_type[core.bits(32) address, integer size, AccessDescriptor accdesc]
    boolean ispair = False;
    return Mem_with_type[address, size, accdesc, ispair];
core.bits(size*8) Mem_with_type[core.bits(32) address, integer size, AccessDescriptor accdesc, boolean ispair]
    assert size IN {1, 2, 4, 8, 16};
    constant halfsize = size DIV 2;
    core.bits(size * 8) value;
    # Check alignment on size of element accessed, not overall access size
    integer alignment = halfsize if ispair else size;
    boolean aligned   = core.IsAligned(address, alignment);
    if not aligned and core.UnalignedAccessFaults(accdesc):
        core.Abort(address, core.AlignmentFault(accdesc));
    if aligned:
        value = AArch32.MemSingle[address, size, accdesc, aligned, ispair];
    else:
        assert size > 1;
        value = core.SetField(value,7,0,AArch32.MemSingle[address, 1, accdesc, aligned]);
        # For subsequent bytes it is CONSTRAINED raise Exception('UNPREDICTABLE') whether an unaligned Device memory
        # access will generate an Alignment Fault, as to get this far means the first byte did
        # not, so we must be changing to a new translation page.
        c = core.ConstrainUnpredictable(Unpredictable_DEVPAGE2);
        assert c IN {Constraint_FAULT, Constraint_NONE};
        if c == Constraint_NONE:
             aligned = True;
        for i = 1 to size-1
            value<8*i+7:8*i> = AArch32.MemSingle[address+i, 1, accdesc, aligned];
    if core.BigEndian(accdesc.acctype):
        value = core.BigEndianReverse(value);
    return value;
# Mem_with_type[] - assignment (write) form
# =========================================
# Perform a write of 'size' bytes. The byte order is reversed for a big-endian access.
Mem_with_type[core.bits(32) address, integer size, AccessDescriptor accdesc] = core.bits(size*8) value_in
    boolean ispair = False;
    Mem_with_type[address, size, accdesc, ispair] = value_in;
Mem_with_type[core.bits(32) address, integer size, AccessDescriptor accdesc,
        boolean ispair] = core.bits(size*8) value_in
    constant halfsize = size DIV 2;
    core.bits(size*8) value = value_in;
    # Check alignment on size of element accessed, not overall access size
    integer alignment = halfsize if ispair else size;
    boolean aligned   = core.IsAligned(address, alignment);
    if not aligned and core.UnalignedAccessFaults(accdesc):
        core.Abort(address, core.AlignmentFault(accdesc));
    if core.BigEndian(accdesc.acctype):
        value = core.BigEndianReverse(value);
    if aligned:
        AArch32.MemSingle[address, size, accdesc, aligned, ispair] = value;
    else:
        assert size > 1;
        AArch32.MemSingle[address, 1, accdesc, aligned] = core.Field(value,7,0);
        # For subsequent bytes it is CONSTRAINED raise Exception('UNPREDICTABLE') whether an unaligned Device memory
        # access will generate an Alignment Fault, as to get this far means the first byte did
        # not, so we must be changing to a new translation page.
        c = core.ConstrainUnpredictable(Unpredictable_DEVPAGE2);
        assert c IN {Constraint_FAULT, Constraint_NONE};
        if c == Constraint_NONE:
             aligned = True;
        for i = 1 to size-1
            AArch32.MemSingle[address+i, 1, accdesc, aligned] = value<8*i+7:8*i>;
    return;
# MemA[] - non-assignment form
# ============================
core.bits(8*size) core.ReadMemA(core.bits(32) address, integer size)
    boolean acqrel = False;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescExLDST(MemOp_LOAD, acqrel, tagchecked);
    return Mem_with_type[address, size, accdesc];
# MemA[] - assignment form
# ========================
core.ReadMemA(core.bits(32) address, integer size) = core.bits(8*size) value
    boolean acqrel = False;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescExLDST(MemOp_STORE, acqrel, tagchecked);
    Mem_with_type[address, size, accdesc] = value;
    return;
# core.CreateAccDescA32LSMD()
# ======================
# Access descriptor for A32 loads/store multiple general purpose registers
AccessDescriptor core.CreateAccDescA32LSMD(MemOp memop)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_GPR);
    accdesc.read            = memop == MemOp_LOAD;
    accdesc.write           = memop == MemOp_STORE;
    accdesc.pan             = True;
    accdesc.a32lsmd         = True;
    accdesc.transactional   = core.HaveTME() and TSTATE.depth > 0;
    return accdesc;
# MemS[] - non-assignment form
# ============================
# Memory accessor for streaming load multiple instructions
core.bits(8*size) core.ReadMemS(core.bits(32) address, integer size)
    AccessDescriptor accdesc = core.CreateAccDescA32LSMD(MemOp_LOAD);
    return Mem_with_type[address, size, accdesc];
# MemS[] - assignment form
# ========================
# Memory accessor for streaming store multiple instructions
core.ReadMemS(core.bits(32) address, integer size) = core.bits(8*size) value
    AccessDescriptor accdesc = core.CreateAccDescA32LSMD(MemOp_STORE);
    Mem_with_type[address, size, accdesc] = value;
    return;
# core.CreateAccDescGPR()
# ==================
# Access descriptor for general purpose register loads/stores
# without exclusive or ordering semantics
AccessDescriptor core.CreateAccDescGPR(MemOp memop, boolean nontemporal, boolean privileged,
                                  boolean tagchecked)
    AccessDescriptor accdesc = core.NewAccDesc(AccessType_GPR);
    accdesc.el              = EL0 if not privileged else core.APSR.EL;
    accdesc.nontemporal     = nontemporal;
    accdesc.read            = memop == MemOp_LOAD;
    accdesc.write           = memop == MemOp_STORE;
    accdesc.pan             = True;
    accdesc.tagchecked      = tagchecked;
    accdesc.transactional   = core.HaveTME() and TSTATE.depth > 0;
    return accdesc;
# MemU[] - non-assignment form
# ============================
core.bits(8*size) core.ReadMemU(core.bits(32) address, integer size)
    boolean nontemporal = False;
    boolean privileged = core.APSR.EL != EL0;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescGPR(MemOp_LOAD, nontemporal, privileged, tagchecked);
    return Mem_with_type[address, size, accdesc];
# MemU[] - assignment form
# ========================
core.ReadMemU(core.bits(32) address, integer size) = core.bits(8*size) value
    boolean nontemporal = False;
    boolean privileged = core.APSR.EL != EL0;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescGPR(MemOp_STORE, nontemporal, privileged, tagchecked);
    Mem_with_type[address, size, accdesc] = value;
    return;
# MemU_unpriv[] - non-assignment form
# ===================================
core.bits(8*size) MemU_unpriv[core.bits(32) address, integer size]
    boolean nontemporal = False;
    boolean privileged = False;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescGPR(MemOp_LOAD, nontemporal, privileged, tagchecked);
    return Mem_with_type[address, size, accdesc];
# MemU_unpriv[] - assignment form
# ===============================
MemU_unpriv[core.bits(32) address, integer size] = core.bits(8*size) value
    boolean nontemporal = False;
    boolean privileged = False;
    boolean tagchecked = False;
    AccessDescriptor accdesc = core.CreateAccDescGPR(MemOp_STORE, nontemporal, privileged, tagchecked);
    Mem_with_type[address, size, accdesc] = value;
    return;
# PC - non-assignment form
# ========================
core.bits(32) PC
    return core.readR(15);               # This includes the offset from AArch32 state
# core.PCStoreValue()
# ==============
core.bits(32) core.PCStoreValue()
    # This function returns the PC value. On architecture versions before Armv7, it
    # is permitted to instead return PC+4, provided it does so consistently. It is
    # used only to describe A32 instructions, so it returns the address of the current
    # instruction plus 8 (normally) or 12 (when the alternative is permitted).
    return PC;
# core.LSR_C()
# =======
(core.bits(N), bit) core.LSR_C(core.bits(N) x, integer shift)
    assert shift > 0 and shift < 256;
    extended_x = core.ZeroExtend(x, shift+N);
    result = extended_x<(shift+N)-1:shift>;
    carry_out = extended_x<shift-1>;
    return (result, carry_out);
# core.LSR()
# =====
core.bits(N) core.LSR(core.bits(N) x, integer shift)
    assert shift >= 0;
    core.bits(N) result;
    if shift == 0:
        result = x;
    else:
        (result, -) = core.LSR_C(x, shift);
    return result;
# core.ROR_C()
# =======
(core.bits(N), bit) core.ROR_C(core.bits(N) x, integer shift)
    assert shift != 0 and shift < 256;
    m = shift MOD N;
    result = core.LSR(x,m) | core.LSL(x,N-m);
    carry_out = result<N-1>;
    return (result, carry_out);
# core.ROR()
# =====
core.bits(N) core.ROR(core.bits(N) x, integer shift)
    assert shift >= 0;
    core.bits(N) result;
    if shift == 0:
        result = x;
    else:
        (result, -) = core.ROR_C(x, shift);
    return result;
# core.RoundDown()
# ===========
integer core.RoundDown(real x);
# core.RoundUp()
# =========
integer core.RoundUp(real x);
# core.RoundTowardsZero()
# ==================
integer core.RoundTowardsZero(real x)
    return 0 if x == 0.0 else core.RoundDown(x) if x >= 0.0 else core.RoundUp(x);
# core.SPSRWriteByInstr()
# ==================
core.SPSRWriteByInstr(core.bits(32) value, core.bits(4) bytemask)
    core.bits(32) new_spsr = SPSR[];
    if core.Bit(bytemask,3) == '1':
        new_spsr = core.SetField(new_spsr,31,24,core.Field(value,31,24));  # N,Z,C,V,Q flags, IT[1:0],J bits
    if core.Bit(bytemask,2) == '1':
        new_spsr = core.SetField(new_spsr,23,16,core.Field(value,23,16));  # IL bit, GE[3:0] flags
    if core.Bit(bytemask,1) == '1':
        new_spsr = core.SetField(new_spsr,15,8,core.Field(value,15,8));    # IT[7:2] bits, E bit, A interrupt mask
    if core.Bit(bytemask,0) == '1':
        new_spsr = core.SetField(new_spsr,7,0,core.Field(value,7,0));      # I,F interrupt masks, T bit, Mode bits
    SPSR[] = new_spsr;                   # raise Exception('UNPREDICTABLE') if User or System mode
    return;
# core.SPSRaccessValid()
# =================
# Checks for MRS (Banked register) or MSR (Banked register) accesses to the SPSRs
# that are raise Exception('UNPREDICTABLE')
core.SPSRaccessValid(core.bits(5) SYSm, core.bits(5) mode)
    case SYSm of
        when '01110'                                                   # SPSR_fiq
            if mode == M32_FIQ  :
                 raise Exception('UNPREDICTABLE');
        when '10000'                                                   # SPSR_irq
            if mode == M32_IRQ  :
                 raise Exception('UNPREDICTABLE');
        when '10010'                                                   # SPSR_svc
            if mode == M32_Svc  :
                 raise Exception('UNPREDICTABLE');
        when '10100'                                                   # SPSR_abt
            if mode == M32_Abort:
                 raise Exception('UNPREDICTABLE');
        when '10110'                                                   # SPSR_und
            if mode == M32_Undef:
                 raise Exception('UNPREDICTABLE');
        when '11100'                                                   # SPSR_mon
            if (not core.HaveEL(EL3) or mode == M32_Monitor or
                core.CurrentSecurityState() != SS_Secure) then raise Exception('UNPREDICTABLE');
        when '11110'                                                   # SPSR_hyp
            if not core.HaveEL(EL2) or mode != M32_Monitor:
                 raise Exception('UNPREDICTABLE');
        otherwise
            raise Exception('UNPREDICTABLE');
    return;
# core.ASR_C()
# =======
(core.bits(N), bit) core.ASR_C(core.bits(N) x, integer shift)
    assert shift > 0 and shift < 256;
    extended_x = core.SignExtend(x, shift+N);
    result = extended_x<(shift+N)-1:shift>;
    carry_out = extended_x<shift-1>;
    return (result, carry_out);
# core.RRX_C()
# =======
(core.bits(N), bit) core.RRX_C(core.bits(N) x, bit carry_in)
    result = carry_in : x<N-1:1>;
    carry_out = core.Bit(x,0);
    return (result, carry_out);
# core.Shift_C()
# =========
(core.bits(N), bit) core.Shift_C(core.bits(N) value, SRType srtype, integer amount, bit carry_in)
    assert not (srtype == 'RRX' and amount != 1);
    core.bits(N) result;
    bit carry_out;
    if amount == 0:
        (result, carry_out) = (value, carry_in);
    else:
        case srtype of
            when 'LSL'
                (result, carry_out) = core.LSL_C(value, amount);
            when 'LSR'
                (result, carry_out) = core.LSR_C(value, amount);
            when 'ASR'
                (result, carry_out) = core.ASR_C(value, amount);
            when 'ROR'
                (result, carry_out) = core.ROR_C(value, amount);
            when 'RRX'
                (result, carry_out) = core.RRX_C(value, carry_in);
    return (result, carry_out);
# core.Shift()
# =======
core.bits(N) core.Shift(core.bits(N) value, SRType srtype, integer amount, bit carry_in)
    (result, -) = core.Shift_C(value, srtype, amount, carry_in);
    return result;
# core.SignedSatQ()
# ============
(core.bits(N), boolean) core.SignedSatQ(integer i, integer N)
    result = 0;
    saturated = False;
    if i > 2^(N-1) - 1:
        result = 2^(N-1) - 1;  saturated = True;
    elsif i < -(2^(N-1)):
        result = -(2^(N-1));  saturated = True;
    else:
        result = i;  saturated = False;
    return (result<N-1:0>, saturated);
# core.SignedSat()
# ===========
core.bits(N) core.SignedSat(integer i, integer N)
    (result, -) = core.SignedSatQ(i, N);
    return result;
# core.T32ExpandImm_C()
# ================
(core.bits(32), bit) core.T32ExpandImm_C(core.bits(12) imm12, bit carry_in)
    imm32 = 0;
    bit carry_out;
    if core.Field(imm12,11,10) == '00':
        case core.Field(imm12,9,8) of
            when '00'
                imm32 = core.ZeroExtend(core.Field(imm12,7,0), 32);
            when '01'
                imm32 = '00000000' : core.Field(imm12,7,0) : '00000000' : core.Field(imm12,7,0);
            when '10'
                imm32 = core.Field(imm12,7,0) : '00000000' : core.Field(imm12,7,0) : '00000000';
            when '11'
                imm32 = core.Field(imm12,7,0) : core.Field(imm12,7,0) : core.Field(imm12,7,0) : core.Field(imm12,7,0);
        carry_out = carry_in;
    else:
        unrotated_value = core.ZeroExtend('1':core.Field(imm12,6,0), 32);
        (imm32, carry_out) = core.ROR_C(unrotated_value, core.UInt(core.Field(imm12,11,7)));
    return (imm32, carry_out);
# core.T32ExpandImm()
# ==============
core.bits(32) core.T32ExpandImm(core.bits(12) imm12)
    # core.APSR.C argument to following function call does not affect the imm32 result.
    (imm32, -) = core.T32ExpandImm_C(imm12, core.APSR.C);
    return imm32;
# core.UnsignedSatQ()
# ==============
(core.bits(N), boolean) core.UnsignedSatQ(integer i, integer N)
    result = 0;
    saturated = False;
    if i > 2^N - 1:
        result = 2^N - 1;  saturated = True;
    elsif i < 0:
        result = 0;  saturated = True;
    else:
        result = i;  saturated = False;
    return (result<N-1:0>, saturated);
# core.UnsignedSat()
# =============
core.bits(N) core.UnsignedSat(integer i, integer N)
    (result, -) = core.UnsignedSatQ(i, N);
    return result;
