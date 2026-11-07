// Harness for RCC mdnsd (mDNSResponder, ARM EXEC @0x10000, Jan 2021 build) — udp/5353 remote parser.
// Target: mDNS_ProcessMessage-class fn @0x27cfc (largest fn, parses DNS header at [buf+6/8/10], cursor at buf+12).
// Input: raw mDNS packet bytes. We call fn(this=m, buf, len, ...) with fake m object.
// EXEC image base 0x10000: map seg1 at 0x10000 (identity), seg2 at 0x7d000.
#include <stdint.h>
typedef unsigned int uint32_t;
typedef unsigned char uint8_t;
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

#define BIN_PATH "/opt/data/cache/scratch/rcc_vnc/mdnsd"

// EXEC: LOAD1 off 0 va 0x10000 filesz 0x5c405 ; LOAD2 off 0x5d000 va 0x7d000 filesz 0x288 memsz 0x20fe4
#define SEG1_VA   0x10000u
#define SEG1_FSZ  0x5d000u
#define SEG1_OFF  0x0
#define SEG2_VA   0x7d000u
#define SEG2_FOFF 0x5d000u
#define SEG2_FSZ  0x1000u
#define SEG2_END  (SEG2_VA + 0x22000u)
// sections: dynsym 0x56c, dynstr 0x5c0ac, rel.dyn 0xf10 (3 entries), rel.plt 0xf28 (0x278/8=79)
#define OFF_DYNSYM 0x56c
#define OFF_DYNSTR 0x5c0ac
#define OFF_RELDYN 0xf10
#define N_RELDYN   3
#define OFF_RELPLT 0xf28
#define N_RELPLT   (0x278/8)

#define ARENA 0x60000000u
#define ARENA_SZ (96u << 20)

extern "C" {
static uint32_t g_bump = ARENA + 0x100000;
static void* bump_alloc(unsigned int sz){ uint32_t c=g_bump; uint32_t n=(c+sz+63)&~63u; if(n>ARENA+ARENA_SZ) return (void*)0; g_bump=n; memset((void*)c,0,sz); return (void*)c; }
static void* my_memmove(void* d, const void* s, unsigned n){ unsigned char* dd=(unsigned char*)d; const unsigned char* ss=(const unsigned char*)s; if(dd<ss){for(unsigned i=0;i<n;i++)dd[i]=ss[i];}else{for(unsigned i=n;i>0;i--)dd[i-1]=ss[i-1];} return d; }
static int my_strcmp(const char* a, const char* b){ while(*a&&*a==*b){a++;b++;} return (unsigned char)*a-(unsigned char)*b; }
static int my_strncmp(const char* a, const char* b, unsigned n){ for(unsigned i=0;i<n;i++){ if(a[i]!=b[i]) return (unsigned char)a[i]-(unsigned char)b[i]; if(!a[i]) return 0;} return 0; }
static char* my_strncpy(char* d, const char* s, unsigned n){ unsigned i=0; for(;i<n&&s[i];i++) d[i]=s[i]; for(;i<n;i++) d[i]=0; return d; }
static int my_memcmp(const void* a, const void* b, unsigned n){ const unsigned char* aa=(const unsigned char*)a; const unsigned char* bb=(const unsigned char*)b; for(unsigned i=0;i<n;i++) if(aa[i]!=bb[i]) return aa[i]-bb[i]; return 0; }
static void* my_memchr(const void* s, int c, unsigned n){ const unsigned char* p=(const unsigned char*)s; for(unsigned i=0;i<n;i++) if(p[i]==(unsigned char)c) return (void*)(p+i); return 0; }
static unsigned my_strlen(const char* s){ unsigned l=0; if(!s) return 0; while(s[l]) l++; return l; }
static unsigned my_strnlen(const char* s, unsigned n){ unsigned l=0; if(!s) return 0; while(l<n&&s[l]) l++; return l; }
static char* my_strdup(const char* s){ unsigned l=my_strlen(s); char* d=(char*)bump_alloc(l+1); for(unsigned i=0;i<=l;i++) d[i]=s[i]; return d; }
static void* my_malloc(unsigned int sz){ return bump_alloc(sz?sz:1); }
static void* my__M_create(void* t, unsigned long* cap){ unsigned long c=cap?*cap:0; if(c>1u<<20)c=1u<<20; return my_malloc((unsigned)(c+1)); }
static void my_free(void* p){ (void)p; }
static void* my_calloc(unsigned n, unsigned sz){ unsigned t=n*sz; void* p=bump_alloc(t?t:1); if(p) memset(p,0,t); return p; }
static void* my_realloc(void* p, unsigned sz){ void* np=bump_alloc(sz?sz:1); if(p&&np) memcpy(np,p,sz<65536?sz:65536); return np; }
static void raw_exit(int c){ register int r0 __asm__("r0")=c; register int r7 __asm__("r7")=248; __asm__ volatile("svc #0"::"r"(r0),"r"(r7):"memory"); for(;;); }
static void my_abort(){ for(;;); }
static int my_printf(const char*, ...){ return 0; }
static int my_fprintf(void*, const char*, ...){ return 0; }
static int my_snprintf(char* b, unsigned sz, const char*, ...){ if(sz>0)b[0]=0; return 0; }
static int my_vsnprintf(char* b, unsigned sz, const char*, void*){ if(sz>0)b[0]=0; return 0; }
static int my_puts(const char*){ return 0; }
static int my_putchar(int c){ return c; }
static int my_getpid(){ return 1; }
static char* my_getenv(const char*){ return 0; }
static int my_socket(int, int, int){ return 3; }
static int my_close(int){ return 0; }
static long my_recv(int, void*, unsigned, int){ return 0; }
static long my_recvmsg(int, void*, int){ return 0; }
static long my_send(int, const void*, unsigned, int){ return 0; }
static long my_sendmsg(int, const void*, int){ return 0; }
static long my_sendto(int, const void*, unsigned, int, const void*, unsigned){ return 0; }
static int my_setsockopt(int, int, int, const void*, unsigned){ return 0; }
static int my_getsockopt(int, int, int, void*, unsigned*){ return 0; }
static int my_bind(int, const void*, unsigned){ return 0; }
static int my_fcntl(int, int, ...){ return 0; }
static int my_select(int, void*, void*, void*, void*){ return 1; }
static int my_poll(void*, unsigned, int){ return 0; }
static int my_ioctl(int, int, ...){ return 0; }
static long my_write(int, const void*, unsigned n){ return n; }
static int my_nanosleep(void*, void*){ return 0; }
static long my_time(long* t){ if(t)*t=0; return 0; }
static int my_clock_gettime(int c, void* ts){ if(ts) memset(ts,0,16); return 0; }
static int my_gettimeofday(void* tv, void* tz){ if(tv) memset(tv,0,16); return 0; }
static void* my_pthread_self(){ return (void*)0x1234; }
static int my_pthread_mutex_lock(void*){ return 0; }
static int my_pthread_mutex_unlock(void*){ return 0; }
static void* my___tls_get_addr(void*){ static char t[256]; return t; }
static int my___cxa_atexit(void*, void*, void*){ return 0; }
static void* my___errno(void){ static int e; return &e; }
static int my_inet_ntop(int, const void*, char*, unsigned){ return 0; }
static unsigned my_inet_addr(const char*){ return 0; }
static void* my_memset(void* d, int c, unsigned n){ return memset(d,c,n); }
__attribute__((naked)) static void stub_ret0(){ __asm__ volatile("mov r0,#0; bx lr"); }
static char* my_strstr_(const char* h, const char* n){ if(!*n) return (char*)h; for(;*h;h++){ const char* a=h; const char* b=n; while(*a&&*b&&*a==*b){a++;b++;} if(!*b) return (char*)h; } return 0; }
static void* lookup_func(const char* n0){
    char nb[256]; int l0=0; while(n0[l0] && n0[l0]!='@' && l0<255){ nb[l0]=n0[l0]; l0++; } nb[l0]=0; const char* n=nb;
    struct E{ const char* n; void* f; };
    static const E tab[]={
        {"memmove",(void*)my_memmove},{"memcpy",(void*)memcpy},{"memset",(void*)memset},
        {"strcmp",(void*)my_strcmp},{"strncmp",(void*)my_strncmp},{"strncpy",(void*)my_strncpy},
        {"memcmp",(void*)my_memcmp},{"memchr",(void*)my_memchr},{"strlen",(void*)my_strlen},{"strnlen",(void*)my_strnlen},
        {"strdup",(void*)my_strdup},{"malloc",(void*)my_malloc},{"free",(void*)my_free},{"calloc",(void*)my_calloc},{"realloc",(void*)my_realloc},
        {"_Znwm",(void*)my_malloc},{"_Znam",(void*)my_malloc},{"_ZdlPv",(void*)my_free},{"_ZdaPv",(void*)my_free},
        {"abort",(void*)my_abort},{"printf",(void*)my_printf},{"fprintf",(void*)my_fprintf},
        {"snprintf",(void*)my_snprintf},{"vsnprintf",(void*)my_vsnprintf},{"puts",(void*)my_puts},{"putchar",(void*)my_putchar},
        {"getpid",(void*)my_getpid},{"getenv",(void*)my_getenv},
        {"socket",(void*)my_socket},{"close",(void*)my_close},{"recv",(void*)my_recv},{"recvmsg",(void*)my_recvmsg},
        {"send",(void*)my_send},{"sendmsg",(void*)my_sendmsg},{"sendto",(void*)my_sendto},
        {"setsockopt",(void*)my_setsockopt},{"getsockopt",(void*)my_getsockopt},{"bind",(void*)my_bind},
        {"fcntl",(void*)my_fcntl},{"select",(void*)my_select},{"poll",(void*)my_poll},{"ioctl",(void*)my_ioctl},
        {"write",(void*)my_write},{"nanosleep",(void*)my_nanosleep},{"time",(void*)my_time},
        {"clock_gettime",(void*)my_clock_gettime},{"gettimeofday",(void*)my_gettimeofday},
        {"pthread_self",(void*)my_pthread_self},{"pthread_mutex_lock",(void*)my_pthread_mutex_lock},{"pthread_mutex_unlock",(void*)my_pthread_mutex_unlock},
        {"__tls_get_addr",(void*)my___tls_get_addr},{"__cxa_atexit",(void*)my___cxa_atexit},{"__errno",(void*)my___errno},
        {"inet_ntop",(void*)my_inet_ntop},{"inet_addr",(void*)my_inet_addr},
    };
    for(unsigned i=0;i<sizeof(tab)/sizeof(tab[0]);i++) if(my_strcmp(tab[i].n,n)==0) return tab[i].f;
    if(my_strstr_(n,"_M_create")) return (void*)my__M_create;
    if(my_strstr_(n,"_Znw")||my_strstr_(n,"_Zna")) return (void*)my_malloc;
    if(my_strstr_(n,"_Zdl")||my_strstr_(n,"_Zda")) return (void*)my_free;
    return 0;
}
} // extern C

// mDNS packet parser (largest fn, reads DNS hdr): VA 0x27cfc
#define T_PROCESS_MSG 0x27cfc

int main(int argc, char** argv){
    if (argc < 2) raw_exit(0);
    static char buf[1<<16];
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) raw_exit(1);
    long n = read(fd, buf, sizeof(buf));
    close(fd);
    if (n < 12) raw_exit(0);
    long plen = n; if (plen > 9000) plen = 9000;  // mDNS max 9000

    int lfd = open(BIN_PATH, O_RDONLY);
    if (lfd < 0) raw_exit(2);
    if (mmap((void*)SEG1_VA, SEG1_FSZ, PROT_READ|PROT_EXEC|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, lfd, SEG1_OFF) == MAP_FAILED) raw_exit(3);
    if (mmap((void*)SEG2_VA, SEG2_FSZ, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, lfd, SEG2_FOFF) == MAP_FAILED) raw_exit(4);
    close(lfd);
    if (mmap((void*)(SEG2_VA+SEG2_FSZ), SEG2_END-(SEG2_VA+SEG2_FSZ), PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) raw_exit(5);
    if (mmap((void*)ARENA, ARENA_SZ, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) raw_exit(10);
    mprotect((void*)(ARENA+0x30000), 0x1000, 0);
    memset((void*)(ARENA+0x80000), 0, 0x10000);

    {
        volatile uint32_t* reldyn = (volatile uint32_t*)(SEG1_VA + OFF_RELDYN);
        volatile uint32_t* relplt = (volatile uint32_t*)(SEG1_VA + OFF_RELPLT);
        volatile uint32_t* dynsym = (volatile uint32_t*)(SEG1_VA + OFF_DYNSYM);
        volatile char* dynstr = (volatile char*)(SEG1_VA + OFF_DYNSTR);
        for (unsigned i=0;i<N_RELDYN;i++){
            uint32_t r_off=reldyn[i*2], r_info=reldyn[i*2+1], rt=r_info&0xff;
            if (rt==23) *(volatile uint32_t*)(r_off) = *(volatile uint32_t*)(r_off);  // EXEC: addend already absolute VA; keep
            else if (rt==21||rt==22) *(volatile uint32_t*)(r_off) = ARENA + 0x80000;  // GLOB_DAT/JUMP_SLOT copy -> scratch
        }
        for (unsigned i=0;i<N_RELPLT;i++){
            uint32_t got=relplt[i*2], r_info=relplt[i*2+1];
            uint32_t sym=r_info>>8;
            const char* name=(const char*)(dynstr + dynsym[sym*4]);
            uint32_t impl=(uint32_t)(uintptr_t)lookup_func(name);
            *(volatile uint32_t*)(got) = impl ? impl : (uint32_t)&stub_ret0;  // EXEC: got VA is absolute
        }
    }

    // packet buffer in arena, NUL-padded
    uint32_t pkt = ARENA + 0x20000;
    memcpy((void*)pkt, buf, plen);
    memset((void*)(pkt+plen), 0, 64);

    // fake mDNS object 'm': big zeroed block in arena, common fields pointed at stub
    uint32_t m = ARENA + 0x2000;
    memset((void*)m, 0, 0x8000);   // mDNS struct is ~8KB+; zero it
    // point some pointer fields at zeroed stub area so derefs are mapped
    for (unsigned off = 4; off < 0x2000; off += 4) *(uint32_t*)(m+off) = ARENA + 0x70000;
    memset((void*)(ARENA+0x70000), 0, 0x10000);

    // call parser: fn(m, pkt, len, flags?) — 0x27cfc reads r1=buf, r2=len?, r3=...
    typedef void (*fn4_t)(void*, void*, void*, void*);
    ((fn4_t)(T_PROCESS_MSG))((void*)m, (void*)pkt, (void*)(uint32_t)plen, (void*)0);
    raw_exit(0);
    return 0;
}
