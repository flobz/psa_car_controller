// Harness RCC MirrorLink SPI plugin: libmirrorlinkspi_so.so (ARM ET_DYN, GCC, dynsym present)
// Targets phone->HU CDB/SBP payload parsers (tcp 36735-36834 usb+):
//   - spi_tclMLVncCdbNaviSink::bDeserializeNaviPayload @0x899d0 (this, u8* data, u32 len, tenNaviObjectType)
//   - spi_tclMLVncCdbSink::bDeserializePayload @0x920c0 (this, VNCCDBSDK*, VNCSBPDeserialize*, u8*, u32)
//   - onDeserialized{String,Int,Bytes,Long,Bool}Data navi/media @0x88b40/0x890bc/0x867f8/0x86530/0x88f30/0x88dc0/0x86968/0x863b4
// Input: [idx LE 2B][payload bytes = deserialized field data]
// Lib mapped at BASE; imports stubbed; fake 'this' objects in ARENA with real vtables.
#include <stdint.h>
typedef unsigned int uint32_t;
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef int int32_t;
#define O_RDONLY 0
#define PROT_READ 1
#define PROT_WRITE 2
#define PROT_EXEC 4
#define MAP_PRIVATE 2
#define MAP_FIXED 16
#define MAP_ANONYMOUS 0x20
#define MAP_FAILED ((void*)-1)
extern "C" int open(const char*, int, ...);
extern "C" long read(int, void*, unsigned int);
extern "C" int close(int);
extern "C" void* mmap(void*, unsigned int, int, int, int, unsigned int);
extern "C" int mprotect(void*, unsigned int, int);
extern "C" void* memset(void*, int, unsigned int);
extern "C" void* memcpy(void*, const void*, unsigned int);

#define LIB_PATH "/opt/data/cache/scratch/rcc_vnc/libmirrorlinkspi_so.so"

// Program headers: LOAD1 va 0 off 0 filesz 0xeaf20 ; LOAD2 va 0xfb000 off 0xeb000 filesz 0x424c memsz 0x6e14
#define BASE      0x50000000u
#define SEG1_VA   BASE
#define SEG1_FSZ  0xeb000u          // page-rounded LOAD1 (0xeaf20)
#define SEG1_OFF  0x0
#define SEG2_VA   (BASE + 0xfb000u)
#define SEG2_FOFF 0xeb000u
#define SEG2_FSZ  0x5000u           // page-rounded 0x424c
#define SEG2_END  (SEG2_VA + 0x8000u) // cover memsz 0x6e14
// Sections (file off == va for seg1; seg2: va = fileoff + 0x10000)
#define OFF_DYNSYM 0x48a8
#define OFF_DYNSTR 0x11498
#define OFF_RELDYN 0x3fce0
#define N_RELDYN   (0x4968/8)
#define OFF_RELPLT 0x44648
#define N_RELPLT   (0x2840/8)

#define ARENA 0x60000000u
#define ARENA_SZ (96u << 20)

extern "C" {

static uint32_t g_bump = ARENA + 0x100000;
static void* bump_alloc(unsigned int sz) {
    uint32_t cur = g_bump;
    uint32_t next = (cur + sz + 63) & ~63u;
    if (next > ARENA + ARENA_SZ) return (void*)0;
    g_bump = next;
    memset((void*)cur, 0, sz);
    return (void*)cur;
}
static void* my_memmove(void* d, const void* s, unsigned int n) {
    unsigned char* dd=(unsigned char*)d; const unsigned char* ss=(const unsigned char*)s;
    if (dd < ss) { for (unsigned i=0;i<n;i++) dd[i]=ss[i]; } else { for (unsigned i=n;i>0;i--) dd[i-1]=ss[i-1]; }
    return d;
}
static int my_strcmp(const char* a, const char* b){ while(*a && *a==*b){a++;b++;} return (unsigned char)*a-(unsigned char)*b; }
static int my_strncmp(const char* a, const char* b, unsigned n){ for(unsigned i=0;i<n;i++){ if(a[i]!=b[i]) return (unsigned char)a[i]-(unsigned char)b[i]; if(a[i]==0) return 0;} return 0; }
static char* my_strncpy(char* d, const char* s, unsigned n){ unsigned i=0; for(;i<n&&s[i];i++) d[i]=s[i]; for(;i<n;i++) d[i]=0; return d; }
static char* my_strcpy(char* d, const char* s){ char* r=d; while((*d++=*s++)); return r; }
static int my_memcmp(const void* a, const void* b, unsigned n){ const unsigned char* aa=(const unsigned char*)a; const unsigned char* bb=(const unsigned char*)b; for(unsigned i=0;i<n;i++) if(aa[i]!=bb[i]) return aa[i]-bb[i]; return 0; }
static void* my_memchr(const void* s, int c, unsigned n){ const unsigned char* p=(const unsigned char*)s; for(unsigned i=0;i<n;i++) if(p[i]==(unsigned char)c) return (void*)(p+i); return 0; }
static char* my_strcat(char* d, const char* s){ char* r=d; while(*d) d++; while((*d++=*s++)); return r; }
static char* my_strchr(const char* s, int c){ while(*s){ if(*s==(char)c) return (char*)s; s++; } return (char)c==0?(char*)s:0; }
static char* my_strrchr(const char* s, int c){ const char* l=0; while(*s){ if(*s==(char)c) l=s; s++; } if((char)c==0) return (char*)s; return (char*)l; }
static char* my_strstr(const char* h, const char* n){ if(!*n) return (char*)h; for(;*h;h++){ const char* hh=h; const char* nn=n; while(*hh&&*nn&&*hh==*nn){hh++;nn++;} if(!*nn) return (char*)h; } return 0; }
static int my_strcasecmp(const char* a, const char* b){ while(*a&&*b){ char ca=*a,cb=*b; if(ca>='A'&&ca<='Z')ca+=32; if(cb>='A'&&cb<='Z')cb+=32; if(ca!=cb) return (unsigned char)ca-(unsigned char)cb; a++;b++; } return (unsigned char)*a-(unsigned char)*b; }
static int my_strncasecmp(const char* a, const char* b, unsigned n){ for(unsigned i=0;i<n;i++){ char ca=a[i],cb=b[i]; if(ca>='A'&&ca<='Z')ca+=32; if(cb>='A'&&cb<='Z')cb+=32; if(ca!=cb) return (unsigned char)ca-(unsigned char)cb; if(ca==0) return 0;} return 0; }
static unsigned my_strlen(const char* s){ unsigned l=0; if(!s) return 0; while(s[l]) l++; return l; }
static unsigned my_strnlen(const char* s, unsigned n){ unsigned l=0; if(!s) return 0; while(l<n&&s[l]) l++; return l; }
static char* my_strdup(const char* s){ unsigned l=my_strlen(s); char* d=(char*)bump_alloc(l+1); for(unsigned i=0;i<=l;i++) d[i]=s[i]; return d; }
static int my_atoi(const char* s){ int r=0,neg=0; while(*s==' '||*s=='\t')s++; if(*s=='-'){neg=1;s++;} else if(*s=='+')s++; while(*s>='0'&&*s<='9'){r=r*10+(*s-'0');s++;} return neg?-r:r; }
static long my_strtol(const char* s, char** e, int base){ long r=0; int neg=0; while(*s==' ')s++; if(*s=='-'){neg=1;s++;} else if(*s=='+')s++; if(base==0){ if(s[0]=='0'&&(s[1]=='x'||s[1]=='X')){base=16;s+=2;} else if(s[0]=='0'){base=8;s++;} else base=10; } while(*s){ int d; if(*s>='0'&&*s<='9')d=*s-'0'; else if(*s>='a'&&*s<='z')d=*s-'a'+10; else if(*s>='A'&&*s<='Z')d=*s-'A'+10; else break; if(d>=base)break; r=r*base+d; s++; } if(e)*e=(char*)s; return neg?-r:r; }
static unsigned long my_strtoul(const char* s, char** e, int base){ return (unsigned long)my_strtol(s,e,base); }
static double my_strtod(const char* s, char** e){ if(e)*e=(char*)s; return 0.0; }
static int my_tolower(int c){ return (c>='A'&&c<='Z')?c+32:c; }
static int my_toupper(int c){ return (c>='a'&&c<='z')?c-32:c; }
static void* my_malloc(unsigned int sz){ return bump_alloc(sz?sz:1); }
static void my_free(void* p){ (void)p; }
static void* my_calloc(unsigned n, unsigned sz){ unsigned t=n*sz; void* p=bump_alloc(t?t:1); if(p) memset(p,0,t); return p; }
static void* my_realloc(void* p, unsigned sz){ void* np=bump_alloc(sz?sz:1); if(p&&np) memcpy(np,p,sz<65536?sz:65536); return np; }
static void my_abort(){ for(;;); }
static void raw_exit(int c){ register int r0 __asm__("r0")=c; register int r7 __asm__("r7")=248; __asm__ volatile("svc #0"::"r"(r0),"r"(r7):"memory"); for(;;); }
static int my_printf(const char*, ...){ return 0; }
static int my_fprintf(void*, const char*, ...){ return 0; }
static int my_sprintf(char* b, const char*, ...){ b[0]=0; return 0; }
static int my_snprintf(char* b, unsigned sz, const char*, ...){ if(sz>0)b[0]=0; return 0; }
static int my_vsnprintf(char* b, unsigned sz, const char*, void*){ if(sz>0)b[0]=0; return 0; }
static int my_vsprintf(char* b, const char*, void*){ b[0]=0; return 0; }
static int my_sscanf(const char*, const char*, ...){ return 0; }
static int my_puts(const char*){ return 0; }
static int my_putchar(int c){ return c; }
static unsigned my_sleep(unsigned s){ return 0; }
static void my_usleep(unsigned){ }
static int my_nanosleep(void*, void*){ return 0; }
static long my_time(long* t){ if(t)*t=0; return 0; }
static int my_clock_gettime(int c, void* ts){ if(ts) memset(ts,0,16); return 0; }
static int my_gettimeofday(void* tv, void* tz){ if(tv) memset(tv,0,16); return 0; }
static char* my_getenv(const char*){ return 0; }
static int my_getpid(){ return 1; }
static int my_getuid(){ return 0; }
static int my_isalnum(int c){ return (c>='0'&&c<='9')||(c>='a'&&c<='z')||(c>='A'&&c<='Z'); }
static int my_isalpha(int c){ return (c>='a'&&c<='z')||(c>='A'&&c<='Z'); }
static int my_isspace(int c){ return c==' '||c=='\t'||c=='\n'||c=='\r'; }
static int my_isupper(int c){ return c>='A'&&c<='Z'; }
static int my_isxdigit(int c){ return (c>='0'&&c<='9')||(c>='a'&&c<='f')||(c>='A'&&c<='F'); }
static int my_rand(){ return 0; }
static void my_srand(unsigned){}
static void my_qsort(void*, unsigned, unsigned, void*){}
static int my_poll(void*, unsigned, int){ return 0; }
static int my_select(int, void*, void*, void*, void*){ return 0; }
static int my_socket(int, int, int){ return 3; }
static int my_close(int){ return 0; }
static long my_recv(int, void*, unsigned, int){ return 0; }
static long my_send(int, const void*, unsigned, int){ return 0; }
static int my_setsockopt(int, int, int, const void*, unsigned){ return 0; }
static int my_fcntl(int, int, ...){ return 0; }
static void* my_pthread_self(){ return (void*)0x1234; }
static int my_pthread_mutex_lock(void*){ return 0; }
static int my_pthread_mutex_unlock(void*){ return 0; }
static int my_pthread_mutex_init(void*, const void*){ return 0; }
static int my_pthread_cond_signal(void*){ return 0; }
static int my_pthread_cond_wait(void*, void*){ return 0; }
static int my_pthread_create(void*, const void*, void*, void*){ return 0; }
static void my_pthread_exit(void*){ raw_exit(0); }
static void* my___tls_get_addr(void* p){ static char tls[256]; return tls; }
static int my___cxa_atexit(void*, void*, void*){ return 0; }
static void* my___errno(void){ static int e; return &e; }
static int my_pipe(int*){ return 0; }
static unsigned my_alarm(unsigned s){ return 0; }
static int my_ioctl(int, int, ...){ return 0; }
static long my_write(int, const void*, unsigned n){ return n; }
static int my_epoll_create(int){ return 4; }
static int my_epoll_ctl(int, int, int, void*){ return 0; }
static int my_epoll_wait(int, void*, int, int){ return 0; }
static int my_eventfd(unsigned, int){ return 5; }
static int my_futex(void*, int, unsigned, void*, void*, unsigned){ return 0; }

static void* my__M_create(void* this_, unsigned long* cap){ unsigned long c = cap ? *cap : 0; if (c > 1<<20) c = 1<<20; return my_malloc((unsigned)(c+1)); }
__attribute__((naked)) static void stub_ret0(){ __asm__ volatile("mov r0,#0; bx lr"); }

static void* lookup_func(const char* n) {
    // strip @GLIBC... version suffix
    static char nb[256];
    unsigned l0=0; while(n[l0] && n[l0]!='@' && l0<255){ nb[l0]=n[l0]; l0++; } nb[l0]=0;
    n = nb;
    struct Ent { const char* n; void* f; };
    static const Ent tab[] = {
        {"memmove",(void*)my_memmove},{"memcpy",(void*)memcpy},{"memset",(void*)memset},
        {"strcmp",(void*)my_strcmp},{"strncmp",(void*)my_strncmp},{"strncpy",(void*)my_strncpy},
        {"strcpy",(void*)my_strcpy},{"memcmp",(void*)my_memcmp},{"memchr",(void*)my_memchr},
        {"strcat",(void*)my_strcat},{"strchr",(void*)my_strchr},{"strrchr",(void*)my_strrchr},
        {"strstr",(void*)my_strstr},{"strcasecmp",(void*)my_strcasecmp},{"strncasecmp",(void*)my_strncasecmp},
        {"strlen",(void*)my_strlen},{"strnlen",(void*)my_strnlen},{"strdup",(void*)my_strdup},
        {"atoi",(void*)my_atoi},{"strtol",(void*)my_strtol},{"strtoul",(void*)my_strtoul},
        {"strtod",(void*)my_strtod},{"tolower",(void*)my_tolower},{"toupper",(void*)my_toupper},
        {"malloc",(void*)my_malloc},{"free",(void*)my_free},{"calloc",(void*)my_calloc},{"realloc",(void*)my_realloc},
        {"_Znwm",(void*)my_malloc},{"_Znam",(void*)my_malloc},{"_ZdlPv",(void*)my_free},{"_ZdaPv",(void*)my_free},
        {"_Znwj",(void*)my_malloc},{"_Znaj",(void*)my_malloc},{"_ZdlPvj",(void*)my_free},{"_ZdaPvj",(void*)my_free},
        {"_ZnwmRKSt9nothrow_t",(void*)my_malloc},{"_ZnamRKSt9nothrow_t",(void*)my_malloc},
        {"_ZdlPvm",(void*)my_free},{"_ZdaPvRKSt9nothrow_t",(void*)my_free},{"_ZdlPvRKSt9nothrow_t",(void*)my_free},
        {"abort",(void*)my_abort},{"printf",(void*)my_printf},{"fprintf",(void*)my_fprintf},
        {"sprintf",(void*)my_sprintf},{"snprintf",(void*)my_snprintf},{"vsnprintf",(void*)my_vsnprintf},
        {"vsprintf",(void*)my_vsprintf},{"sscanf",(void*)my_sscanf},{"puts",(void*)my_puts},{"putchar",(void*)my_putchar},
        {"sleep",(void*)my_sleep},{"usleep",(void*)my_usleep},{"nanosleep",(void*)my_nanosleep},
        {"time",(void*)my_time},{"clock_gettime",(void*)my_clock_gettime},{"gettimeofday",(void*)my_gettimeofday},
        {"getenv",(void*)my_getenv},{"getpid",(void*)my_getpid},{"getuid",(void*)my_getuid},
        {"isalnum",(void*)my_isalnum},{"isalpha",(void*)my_isalpha},{"isspace",(void*)my_isspace},
        {"isupper",(void*)my_isupper},{"isxdigit",(void*)my_isxdigit},{"rand",(void*)my_rand},{"srand",(void*)my_srand},
        {"qsort",(void*)my_qsort},{"poll",(void*)my_poll},{"select",(void*)my_select},
        {"socket",(void*)my_socket},{"close",(void*)my_close},{"recv",(void*)my_recv},{"send",(void*)my_send},
        {"setsockopt",(void*)my_setsockopt},{"fcntl",(void*)my_fcntl},{"pthread_self",(void*)my_pthread_self},
        {"pthread_mutex_lock",(void*)my_pthread_mutex_lock},{"pthread_mutex_unlock",(void*)my_pthread_mutex_unlock},
        {"pthread_mutex_init",(void*)my_pthread_mutex_init},{"pthread_cond_signal",(void*)my_pthread_cond_signal},
        {"pthread_cond_wait",(void*)my_pthread_cond_wait},{"pthread_create",(void*)my_pthread_create},
        {"pthread_exit",(void*)my_pthread_exit},{"__tls_get_addr",(void*)my___tls_get_addr},
        {"__cxa_atexit",(void*)my___cxa_atexit},{"__errno",(void*)my___errno},{"pipe",(void*)my_pipe},
        {"alarm",(void*)my_alarm},{"ioctl",(void*)my_ioctl},{"write",(void*)my_write},
        {"epoll_create",(void*)my_epoll_create},{"epoll_ctl",(void*)my_epoll_ctl},{"epoll_wait",(void*)my_epoll_wait},
        {"eventfd",(void*)my_eventfd},{"futex",(void*)my_futex},
    };
    for (unsigned i=0;i<sizeof(tab)/sizeof(tab[0]);i++) if (my_strcmp(tab[i].n,n)==0) return tab[i].f;
    // mangled C++ names often appear too; match suffix
    unsigned l = my_strlen(n);
    for (unsigned i=0;i<sizeof(tab)/sizeof(tab[0]);i++) {
        unsigned m = my_strlen(tab[i].n);
        if (l>=m && my_strcmp(n+l-m, tab[i].n)==0) return tab[i].f;
    }
    // C++ runtime helpers that return heap pointers -> malloc-backed; else stub
    if (my_strstr(n,"_M_create")) return (void*)my__M_create;
    if (my_strstr(n,"_Znw") || my_strstr(n,"_Zna") || (my_strstr(n,"basic_string") && my_strstr(n,"_M_"))) return (void*)my_malloc;
    if (my_strstr(n,"_Zdl") || my_strstr(n,"_Zda") || my_strstr(n,"_M_dispose") || my_strstr(n,"_M_destroy")) return (void*)my_free;
    return 0;
}

} // extern C

// target fns (lib VA)
#define T_NAVI_PAYLOAD   0x899d0  // bDeserializeNaviPayload(this, const u8*, u32 len, tenNaviObjectType)
#define T_CDB_PAYLOAD    0x920c0  // bDeserializePayload(this, VNCCDBSDK*, VNCSBPDeserialize*, const u8*, u32)
#define T_NAVI_STR       0x88b40  // onDeserializedStringData(this, u32 id, const char*, u32 len)
#define T_NAVI_INT       0x890bc  // onDeserializedIntData(this, u32 id, int)
#define T_NAVI_LONG      0x88f30  // onDeserializedLongData(this, u32, long long)
#define T_NAVI_BOOL      0x88dc0  // onDeserializedBoolData(this, u32, int)
#define T_MEDIA_STR      0x86530
#define T_MEDIA_BYTES    0x867f8  // onDeserializedBytesData(this, u32, const s8*, u32)
#define T_MEDIA_BYTE     0x86968
#define T_MEDIA_INT      0x863b4

int main(int argc, char** argv){
    if (argc < 2) raw_exit(0);
    static char buf[1<<16];
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) raw_exit(1);
    long n = read(fd, buf, sizeof(buf));
    close(fd);
    if (n < 3) raw_exit(0);
    unsigned idx = (uint8_t)buf[0] | ((uint8_t)buf[1] << 8);
    if (idx > 9) raw_exit(0);

    int lfd = open(LIB_PATH, O_RDONLY);
    if (lfd < 0) raw_exit(2);
    if (mmap((void*)SEG1_VA, SEG1_FSZ, PROT_READ|PROT_EXEC|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, lfd, SEG1_OFF) == MAP_FAILED) raw_exit(3);
    if (mmap((void*)SEG2_VA, SEG2_FSZ, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, lfd, SEG2_FOFF) == MAP_FAILED) raw_exit(4);
    close(lfd);
    if (mmap((void*)(SEG2_VA+SEG2_FSZ), SEG2_END-(SEG2_VA+SEG2_FSZ), PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) raw_exit(5);
    if (mmap((void*)ARENA, ARENA_SZ, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) raw_exit(10);
    // guard page after a 64KB scratch buffer at ARENA+0x20000 (decoders may write there)
    mprotect((void*)(ARENA+0x30000), 0x1000, 0);
    memset((void*)(ARENA+0x80000), 0, 0x10000);

    {
        volatile uint32_t* reldyn = (volatile uint32_t*)(SEG1_VA + OFF_RELDYN);
        volatile uint32_t* relplt = (volatile uint32_t*)(SEG1_VA + OFF_RELPLT);
        volatile uint32_t* dynsym = (volatile uint32_t*)(SEG1_VA + OFF_DYNSYM);
        volatile char* dynstr = (volatile char*)(SEG1_VA + OFF_DYNSTR);
        for (unsigned i=0;i<N_RELDYN;i++){
            uint32_t r_offset = reldyn[i*2];
            uint32_t r_info = reldyn[i*2+1];
            uint32_t rtype = r_info & 0xff;
            uint32_t slot = BASE + r_offset;
            if (rtype == 23) {
                *(volatile uint32_t*)slot = BASE + *(volatile uint32_t*)slot;
            } else if (rtype == 21 || rtype == 22) {
                *(volatile uint32_t*)slot = ARENA + 0x80000;
            }
        }
        for (unsigned i=0;i<N_RELPLT;i++){
            uint32_t got = relplt[i*2];
            uint32_t r_info = relplt[i*2+1];
            uint32_t sym_idx = r_info >> 8;
            const char* name = (const char*)(dynstr + dynsym[sym_idx*4]);
            uint32_t impl = (uint32_t)(uintptr_t)lookup_func(name);
            *(volatile uint32_t*)(BASE + got) = impl ? impl : (uint32_t)&stub_ret0;
        }
    }

    const char* payload = buf + 2;
    long plen = n - 2;
    if (plen > 60000) plen = 60000;
    if (plen < 0) plen = 0;
    uint32_t data = ARENA + 0x20000;   // payload buffer inside guarded region
    memcpy((void*)data, payload, plen);
    ((char*)data)[plen] = 0;  // NUL-terminate: SBP strings are NUL-terminated by the deserializer
    // place a second copy right after for len overreads within guard window
    // (guard at ARENA+0x30000 catches writes/reads past 64KB)

    // generic stub vtable + objects
    uint32_t stub_vt = ARENA + 0x70000;
    for (int i = 0; i < 256; i++) *(uint32_t*)(stub_vt + i*4) = (uint32_t)&stub_ret0;
    uint32_t stub_obj = ARENA + 0x71000;
    memset((void*)stub_obj, 0, 0x800);
    *(uint32_t*)(stub_obj+0) = stub_vt;
    for (unsigned off = 4; off < 0x800; off += 4) *(uint32_t*)(stub_obj+off) = (uint32_t)&stub_ret0;
    // extra stub obj for deep fields
    uint32_t stub2 = ARENA + 0x72000;
    memset((void*)stub2, 0, 0x400);
    *(uint32_t*)(stub2+0) = stub_vt;
    for (unsigned off = 4; off < 0x400; off += 4) *(uint32_t*)(stub2+off) = (uint32_t)&stub_ret0;

    // fake 'this' sink object: 0x400 bytes, [0]=stub_vt (real class vtable unknown -> stub),
    // pointer fields -> stub2 so virtual calls land on stub_ret0
    uint32_t this_obj = ARENA + 0x2000;
    memset((void*)this_obj, 0, 0x800);
    *(uint32_t*)(this_obj+0) = stub_vt;
    for (unsigned off = 4; off < 0x800; off += 4) *(uint32_t*)(this_obj+off) = stub2;

    typedef void (*fn5_t)(void*, void*, void*, void*, void*);
    typedef int  (*fn4r_t)(void*, void*, void*, void*);

    switch (idx) {
    case 0: // bDeserializeNaviPayload(this, data, len, objtype=payload-driven)
        ((fn5_t)(BASE+T_NAVI_PAYLOAD))((void*)this_obj, (void*)data, (void*)(uint32_t)plen, (void*)(uint32_t)(plen>0?(uint8_t)payload[0]:0), (void*)0);
        break;
    case 1: // bDeserializePayload(this, cdbSDK=stub, sbpDeser=stub, data, len)
        ((fn5_t)(BASE+T_CDB_PAYLOAD))((void*)this_obj, (void*)stub_obj, (void*)stub2, (void*)data, (void*)(uint32_t)plen);
        break;
    case 2: // navi onDeserializedStringData(this, id, ptr, len): id from payload[0..3]
        ((fn5_t)(BASE+T_NAVI_STR))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)data, (void*)(uint32_t)(plen>4?plen-4:0), (void*)0);
        break;
    case 3: // navi onDeserializedIntData(this, id, int val)
        ((fn5_t)(BASE+T_NAVI_INT))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)(uint32_t)(plen>4?(int32_t)(((uint8_t)payload[4]<<24)|((uint8_t)payload[5]<<16)|((uint8_t)payload[6]<<8)|(uint8_t)payload[7]):0), (void*)0, (void*)0);
        break;
    case 4: // navi onDeserializedBytesData-like via media bytes (this, id, ptr, len)
        ((fn5_t)(BASE+T_MEDIA_BYTES))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)data, (void*)(uint32_t)(plen>4?plen-4:0), (void*)0);
        break;
    case 5: // media onDeserializedStringData
        ((fn5_t)(BASE+T_MEDIA_STR))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)data, (void*)(uint32_t)(plen>4?plen-4:0), (void*)0);
        break;
    case 6: // navi onDeserializedLongData(this, id, long long)
        ((fn5_t)(BASE+T_NAVI_LONG))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)0, (void*)0, (void*)0);
        break;
    case 7: // navi onDeserializedBoolData(this, id, int)
        ((fn5_t)(BASE+T_NAVI_BOOL))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)(uint32_t)(plen>4?(int32_t)(((uint8_t)payload[4]<<24)|((uint8_t)payload[5]<<16)|((uint8_t)payload[6]<<8)|(uint8_t)payload[7]):0), (void*)0, (void*)0);
        break;
    case 8: // media onDeserializedByteData(this, id, s8)
        ((fn5_t)(BASE+T_MEDIA_BYTE))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)(uint32_t)(plen>4?(uint8_t)payload[4]:0), (void*)0, (void*)0);
        break;
    case 9: // media onDeserializedIntData(this, id, int)
        ((fn5_t)(BASE+T_MEDIA_INT))((void*)this_obj, (void*)(uint32_t)(plen>=4?((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3]:0), (void*)(uint32_t)(plen>4?(int32_t)(((uint8_t)payload[4]<<24)|((uint8_t)payload[5]<<16)|((uint8_t)payload[6]<<8)|(uint8_t)payload[7]):0), (void*)0, (void*)0);
        break;
    }
    raw_exit(0);
    return 0;
}
