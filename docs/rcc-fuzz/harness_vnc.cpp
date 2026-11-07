// Harness RCC RealVNC Automotive viewer SDK: libvncviewersdk.so.0.0.0 (ARM ET_DYN, stripped, GCC 4.4.4)
// Targets the RFB *client-side* rect parsers = CVE-2008-4770 class (malicious VNC server -> RCE on viewer).
// Loads lib at base 0x50000000, applies R_ARM_RELATIVE with delta, patches GOT: libc->harness impls,
// undefined non-libc -> stub_ret0. Input: [idx LE 2B][payload = fake RFB stream bytes].
#include <stdint.h>
typedef unsigned int uint32_t;
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef short int16_t;
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

#define LIB_PATH "/opt/data/cache/scratch/rcc_vnc/libvncviewersdk.so.0.0.0"

// Program headers: LOAD1 va 0 off 0 filesz 0x253550 ; LOAD2 va 0x25c460 off 0x254460 filesz 0x180e8 memsz 0x1fe10
#define BASE      0x50000000u
#define SEG1_VA   BASE
#define SEG1_FSZ  0x254000u          // page-rounded file part (covers LOAD1 0x253550)
#define SEG1_OFF  0x0
#define SEG2_VA   (BASE + 0x25c000u)  // page-align 0x25c460
#define SEG2_FOFF 0x254000u
#define SEG2_FSZ  0x19000u            // page-rounded (0x180e8 -> 0x19000)
#define SEG2_END  (SEG2_VA + 0x21000u)  // cover full memsz 0x1fe10 + margin
// Section offsets (file off == va for seg1):
#define OFF_DYNSYM 0x7bc
#define OFF_DYNSTR 0x156c
#define OFF_RELDYN 0x22a0
#define N_RELDYN   (0x18f70/8)
#define OFF_RELPLT 0x1b210
#define N_RELPLT   (0x688/8)
#define GOT_VA     0x26e000u

#define ARENA 0x60000000u
#define ARENA_SZ (96u << 20)

extern "C" {

static uint32_t g_bump = ARENA + 0x100000;
static void* bump_alloc(unsigned int sz) {
    uint32_t cur = g_bump;
    uint32_t next = (cur + sz + 63) & ~63u;
    if (next > ARENA + ARENA_SZ) return (void*)0;
    g_bump = next;
    memset((void*)cur, 0, sz);   // zero like calloc: no garbage pointers
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
static void* my__M_create(void* this_, unsigned long* cap){ unsigned long c = cap ? *cap : 0; if (c > 1u<<20) c = 1u<<20; return my_malloc((unsigned)(c+1)); }
static void my_free(void* p){ (void)p; }
static void* my_calloc(unsigned n, unsigned sz){ unsigned t=n*sz; void* p=bump_alloc(t?t:1); if(p) memset(p,0,t); return p; }
static void* my_realloc(void* p, unsigned sz){ void* np=bump_alloc(sz?sz:1); if(p&&np) memcpy(np,p,sz<65536?sz:65536); return np; }
static void my_abort(){ for(;;); }
static void my_exit(int c){ register int r0 __asm__("r0")=c; register int r7 __asm__("r7")=248; __asm__ volatile("svc #0"::"r"(r0),"r"(r7):"memory"); for(;;); }
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
static int my_socket(int, int, int){ return -1; }
static int my_connect(int, void*, unsigned){ return -1; }
static long my_read(int fd, void* b, unsigned n){ return 0; }
static long my_write(int fd, const void* b, unsigned n){ return n; }
static int my_close(int){ return 0; }
static int my_open(const char*, int, ...){ return -1; }
static int my_fcntl(int, int, ...){ return 0; }
static int my_ioctl(int, int, ...){ return 0; }
static int my_pthread_mutex_lock(void*){ return 0; }
static int my_pthread_mutex_unlock(void*){ return 0; }
static int my_pthread_mutex_init(void*, void*){ return 0; }
static int my_pthread_mutex_destroy(void*){ return 0; }
static int my_pthread_cond_init(void*, void*){ return 0; }
static int my_pthread_cond_destroy(void*){ return 0; }
static int my_pthread_cond_wait(void*, void*){ return 0; }
static int my_pthread_cond_signal(void*){ return 0; }
static int my_pthread_cond_broadcast(void*){ return 0; }
static int my_pthread_create(void*, void*, void*, void*){ return 0; }
static int my_pthread_join(void*, void**){ return 0; }
static int my_pthread_once(void*, void*){ return 0; }
static void* my_pthread_self(){ return (void*)0; }
// TLS: return a zeroed 256-byte TLS block; lib uses __tls_get_addr for its TLS vars
static char g_tls[256] __attribute__((aligned(8)));
static void* my_tls_get_addr(void*){ memset(g_tls,0,sizeof(g_tls)); return g_tls; }
static int my_pthread_key_create(void*, void*){ return 0; }
static void* my_pthread_getspecific(unsigned){ return 0; }
static int my_pthread_setspecific(unsigned, void*){ return 0; }
static int my_pthread_key_delete(unsigned){ return 0; }
static int my_pthread_cancel(void*){ return 0; }
static int my_pthread_sigmask(int, void*, void*){ return 0; }
static int my_setlocale(int, const char*){ return 0; }
static void* my___errno_location(){ static int e; return &e; }
static int my_dlopen(const char*, int){ return 0; }
static void* my_dlsym(void*, const char*){ return 0; }
static char* my_dlerror(){ return 0; }
static int my_dlclose(void*){ return 0; }
static int my___memcpy_chk(void* d, const void* s, unsigned n, unsigned){ memcpy(d,s,n); return 0; }
static int my___memset_chk(void* d, int c, unsigned n, unsigned){ memset(d,c,n); return 0; }
static int my___sprintf_chk(char* b, int, unsigned, const char*, ...){ b[0]=0; return 0; }
static int my___vsnprintf_chk(char* b, unsigned sz, unsigned, const char*, void*){ if(sz>0)b[0]=0; return 0; }
static char* my___strcat_chk(char* d, const char* s, unsigned){ return my_strcat(d,s); }
static int my___fxstat(int, int, void*){ return 0; }
static int my___fxstat64(int, int, void*){ return 0; }
static int my___xstat(int, const char*, void*){ return 0; }
static long my_lseek64(int, long, int){ return 0; }
static int my_fseeko(void*, long, int){ return 0; }
static long my_ftello(void*){ return 0; }
static void* my_fopen(const char*, const char*){ return 0; }
static void* my_fopen64(const char*, const char*){ return 0; }
static int my_fclose(void*){ return 0; }
static unsigned my_fread(void* b, unsigned, unsigned, void*){ return 0; }
static unsigned my_fwrite(const void*, unsigned, unsigned, void*){ return 0; }
static int my_fgets(char*, int, void*){ return 0; }
static int my_feof(void*){ return 1; }
static int my_ferror(void*){ return 0; }
static int my_fflush(void*){ return 0; }
static int my_fputc(int, void*){ return 0; }
static int my_fputs(const char*, void*){ return 0; }
static int my_fileno(void*){ return -1; }
static void* my_fdopen(int, const char*){ return 0; }
static int my_mkstemp(char*){ return -1; }
static int my_remove(const char*){ return 0; }
static int my_rename(const char*, const char*){ return 0; }
static int my_pipe(int*){ return 0; }
static int my_chmod(const char*, unsigned){ return 0; }
static unsigned my_umask(unsigned){ return 0; }
static int my_prctl(int, ...){ return 0; }
static long my_writev(int, void*, int){ return 0; }
static int my_floor_dummy(){ return 0; }
static double my_pow(double, double){ return 0; }
static double my_floor(double x){ return x < 0 ? -1.0 : 0.0; }
static double my_frexp(double, int*){ return 0; }
static double my_modf(double, double*){ return 0; }
static void* my_gmtime(void*){ return 0; }
static void* my_localtime(void*){ return 0; }
static long my_mktime(void*){ return 0; }
static unsigned my_strftime(char*, unsigned, const char*, void*){ return 0; }
static int my_strcoll(const char*, const char*){ return 0; }
static unsigned my_strxfrm(char*, const char*, unsigned){ return 0; }
static unsigned my_strcspn(const char*, const char*){ return 0; }
static unsigned my_strspn(const char*, const char*){ return 0; }
static char* my_strpbrk(const char* s, const char* set){ for(;*s;s++){ for(const char* p=set;*p;p++) if(*p==*s) return (char*)s; } return 0; }
static unsigned my_wcslen(const wchar_t* s){ unsigned l=0; if(s) while(s[l]) l++; return l; }
static void* my_wmemchr(const wchar_t*, int, unsigned){ return 0; }
static int my_wmemcmp(const wchar_t*, const wchar_t*, unsigned){ return 0; }
static wchar_t* my_wmemcpy(wchar_t* d, const wchar_t* s, unsigned n){ for(unsigned i=0;i<n;i++) d[i]=s[i]; return d; }
static wchar_t* my_wmemmove(wchar_t* d, const wchar_t* s, unsigned n){ for(unsigned i=0;i<n;i++) d[i]=s[i]; return d; }
static wchar_t* my_wmemset(wchar_t* d, int c, unsigned n){ for(unsigned i=0;i<n;i++) d[i]=c; return d; }
static int my_wctype(const char*){ return 0; }
static int my_iswctype(int, int){ return 0; }
static int my_btowc(int c){ return c; }
static int my_wctob(int c){ return c; }
static int my_mbrtowc(void*, const char*, unsigned, void*){ return 0; }
static int my_wcrtomb(char*, int, void*){ return 0; }
static int my_strerror_dummy(){ return 0; }
static char* my_strerror(int e){ return (char*)""; }
static int my_setvbuf(void*, char*, int, unsigned){ return 0; }
static int my_clearerr(void*){ return 0; }
static int my_sigemptyset(void*){ return 0; }
static int my_sigaddset(void*, int){ return 0; }
static int my_longjmp_chk(void*, int){ for(;;); }
static int my__setjmp(void*){ return 0; }
static void my__cxa_atexit(void*, void*, void*){ }
static void my__cxa_finalize(void*){ }
static void my__gmon_start__(){ }
static int my___ctype_get_mb_cur_max(){ return 1; }

static int16_t ctype_b[384];
static int32_t ctype_lower[384];
static int32_t ctype_upper[384];
static void init_ctype(){
    for (int i=0;i<384;i++){
        int c=i-128; int flags=0;
        if (c>='a'&&c<='z') flags|=0x0200|0x0100|0x0008;
        if (c>='A'&&c<='Z') flags|=0x0400|0x0100|0x0008;
        if (c>='0'&&c<='9') flags|=0x0800|0x0100|0x0008;
        ctype_b[i]=(int16_t)flags;
        ctype_lower[i]=(c>='A'&&c<='Z')?c+32:c;
        ctype_upper[i]=(c>='a'&&c<='z')?c-32:c;
    }
}
static int16_t* ctype_b_ptr = ctype_b+128;
static int32_t* ctype_lower_ptr = ctype_lower+128;
static int32_t* ctype_upper_ptr = ctype_upper+128;
static void** my_ctype_b_loc(){ init_ctype(); return (void**)&ctype_b_ptr; }
static void** my_ctype_tolower_loc(){ init_ctype(); return (void**)&ctype_lower_ptr; }
static void** my_ctype_toupper_loc(){ init_ctype(); return (void**)&ctype_upper_ptr; }

static uint32_t stub_ret0(){ return 0; }

// ---- fake RFB stream feeder ----
// The lib's input "stream" object: [0]=vtable, [4]=cur ptr, [8]=end ptr.
// Low-level read is stream->vt[0x20] (fn idx 8): read(stream, buf, len) -> bool (1=ok).
// readExact helper 0xba2e0(stream, dest, len) calls vt[0x20] and vt[0xc] (ensure).
static char g_stream[1<<16];
static uint32_t g_stream_len=0, g_stream_pos=0;
// fn8: r0=stream, r1=buf, r2=len -> returns 1 ok / 0 fail
static int stream_read(void* stream, void* buf, unsigned len){
    (void)stream;
    uint32_t rem = g_stream_len - g_stream_pos;
    uint32_t n = len < rem ? len : rem;
    if (n && buf) memcpy(buf, g_stream + g_stream_pos, n);
    g_stream_pos += n;
    return 1;  // always "ok"; at EOF n=0 so callee's buffer stays zeroed and its loop exits
}
static int stream_ensure(void* stream, void* buf, unsigned len){ (void)stream;(void)buf;(void)len; return 1; }

} // extern "C"

static void raw_exit(int code){
    register int r0 __asm__("r0")=code; register int r7 __asm__("r7")=248;
    __asm__ volatile("svc #0"::"r"(r0),"r"(r7):"memory"); for(;;);
}

struct func_map_t { const char* name; uint32_t addr; };
static func_map_t func_map[] = {
    {"memset",(uint32_t)&memset},{"memcpy",(uint32_t)&memcpy},{"memmove",(uint32_t)&my_memmove},
    {"memchr",(uint32_t)&my_memchr},{"memcmp",(uint32_t)&my_memcmp},{"strlen",(uint32_t)&my_strlen},
    {"strnlen",(uint32_t)&my_strnlen},{"strcmp",(uint32_t)&my_strcmp},{"strncmp",(uint32_t)&my_strncmp},
    {"strncpy",(uint32_t)&my_strncpy},{"strcpy",(uint32_t)&my_strcpy},{"strcat",(uint32_t)&my_strcat},
    {"strchr",(uint32_t)&my_strchr},{"strrchr",(uint32_t)&my_strrchr},{"strstr",(uint32_t)&my_strstr},
    {"strcasecmp",(uint32_t)&my_strcasecmp},{"strncasecmp",(uint32_t)&my_strncasecmp},
    {"strdup",(uint32_t)&my_strdup},{"__strdup",(uint32_t)&my_strdup},
    {"atoi",(uint32_t)&my_atoi},{"strtol",(uint32_t)&my_strtol},{"strtoul",(uint32_t)&my_strtoul},
    {"strtod",(uint32_t)&my_strtod},{"strtof",(uint32_t)&my_strtod},{"strtold",(uint32_t)&my_strtod},
    {"tolower",(uint32_t)&my_tolower},{"toupper",(uint32_t)&my_toupper},
    {"malloc",(uint32_t)&my_malloc},{"free",(uint32_t)&my_free},{"calloc",(uint32_t)&my_calloc},
    {"realloc",(uint32_t)&my_realloc},{"abort",(uint32_t)&my_abort},{"exit",(uint32_t)&my_exit},{"_exit",(uint32_t)&my_exit},
    {"_Znwm",(uint32_t)&my_malloc},{"_Znam",(uint32_t)&my_malloc},{"_ZdlPv",(uint32_t)&my_free},{"_ZdaPv",(uint32_t)&my_free},
    {"_Znwj",(uint32_t)&my_malloc},{"_Znaj",(uint32_t)&my_malloc},{"_ZdlPvj",(uint32_t)&my_free},{"_ZdaPvj",(uint32_t)&my_free},
    {"_ZnwmRKSt9nothrow_t",(uint32_t)&my_malloc},{"_ZnamRKSt9nothrow_t",(uint32_t)&my_malloc},
    {"_ZdlPvm",(uint32_t)&my_free},{"_ZdlPvmRKSt9nothrow_t",(uint32_t)&my_free},{"_ZdaPvm",(uint32_t)&my_free},
    {"printf",(uint32_t)&my_printf},{"fprintf",(uint32_t)&my_fprintf},{"sprintf",(uint32_t)&my_sprintf},
    {"snprintf",(uint32_t)&my_snprintf},{"vsnprintf",(uint32_t)&my_vsnprintf},{"vsprintf",(uint32_t)&my_vsprintf},
    {"sscanf",(uint32_t)&my_sscanf},{"puts",(uint32_t)&my_puts},{"putchar",(uint32_t)&my_putchar},
    {"sleep",(uint32_t)&my_sleep},{"usleep",(uint32_t)&my_usleep},{"nanosleep",(uint32_t)&my_nanosleep},
    {"time",(uint32_t)&my_time},{"clock_gettime",(uint32_t)&my_clock_gettime},{"gettimeofday",(uint32_t)&my_gettimeofday},
    {"__ctype_b_loc",(uint32_t)&my_ctype_b_loc},{"__ctype_tolower_loc",(uint32_t)&my_ctype_tolower_loc},
    {"__ctype_toupper_loc",(uint32_t)&my_ctype_toupper_loc},{"__ctype_get_mb_cur_max",(uint32_t)&my___ctype_get_mb_cur_max},
    {"getenv",(uint32_t)&my_getenv},{"getpid",(uint32_t)&my_getpid},{"getuid",(uint32_t)&my_getuid},
    {"isalnum",(uint32_t)&my_isalnum},{"isalpha",(uint32_t)&my_isalpha},{"isspace",(uint32_t)&my_isspace},
    {"isupper",(uint32_t)&my_isupper},{"isxdigit",(uint32_t)&my_isxdigit},
    {"rand",(uint32_t)&my_rand},{"srand",(uint32_t)&my_srand},{"qsort",(uint32_t)&my_qsort},
    {"poll",(uint32_t)&my_poll},{"select",(uint32_t)&my_select},{"socket",(uint32_t)&my_socket},
    {"connect",(uint32_t)&my_connect},{"read",(uint32_t)&my_read},{"write",(uint32_t)&my_write},
    {"writev",(uint32_t)&my_writev},{"close",(uint32_t)&my_close},{"open",(uint32_t)&my_open},
    {"fcntl",(uint32_t)&my_fcntl},{"ioctl",(uint32_t)&my_ioctl},
    {"pthread_mutex_lock",(uint32_t)&my_pthread_mutex_lock},{"pthread_mutex_unlock",(uint32_t)&my_pthread_mutex_unlock},
    {"pthread_mutex_init",(uint32_t)&my_pthread_mutex_init},{"pthread_mutex_destroy",(uint32_t)&my_pthread_mutex_destroy},
    {"pthread_cond_init",(uint32_t)&my_pthread_cond_init},{"pthread_cond_destroy",(uint32_t)&my_pthread_cond_destroy},
    {"pthread_cond_wait",(uint32_t)&my_pthread_cond_wait},{"pthread_cond_signal",(uint32_t)&my_pthread_cond_signal},
    {"pthread_cond_broadcast",(uint32_t)&my_pthread_cond_broadcast},{"pthread_cond_timedwait",(uint32_t)&my_pthread_cond_wait},
    {"pthread_create",(uint32_t)&my_pthread_create},{"pthread_join",(uint32_t)&my_pthread_join},
    {"pthread_once",(uint32_t)&my_pthread_once},{"pthread_self",(uint32_t)&my_pthread_self},
    {"pthread_key_create",(uint32_t)&my_pthread_key_create},{"pthread_getspecific",(uint32_t)&my_pthread_getspecific},
    {"pthread_setspecific",(uint32_t)&my_pthread_setspecific},{"pthread_key_delete",(uint32_t)&my_pthread_key_delete},
    {"pthread_cancel",(uint32_t)&my_pthread_cancel},{"pthread_sigmask",(uint32_t)&my_pthread_sigmask},
    {"setlocale",(uint32_t)&my_setlocale},{"__errno_location",(uint32_t)&my___errno_location},
    {"dlopen",(uint32_t)&my_dlopen},{"dlsym",(uint32_t)&my_dlsym},{"dlerror",(uint32_t)&my_dlerror},{"dlclose",(uint32_t)&my_dlclose},
    {"__memcpy_chk",(uint32_t)&my___memcpy_chk},{"__memset_chk",(uint32_t)&my___memset_chk},
    {"__sprintf_chk",(uint32_t)&my___sprintf_chk},{"__vsnprintf_chk",(uint32_t)&my___vsnprintf_chk},
    {"__strcat_chk",(uint32_t)&my___strcat_chk},
    {"__fxstat",(uint32_t)&my___fxstat},{"__fxstat64",(uint32_t)&my___fxstat64},{"__xstat",(uint32_t)&my___xstat},
    {"lseek64",(uint32_t)&my_lseek64},{"fseeko",(uint32_t)&my_fseeko},{"ftello",(uint32_t)&my_ftello},
    {"fopen",(uint32_t)&my_fopen},{"fopen64",(uint32_t)&my_fopen64},{"fclose",(uint32_t)&my_fclose},
    {"fread",(uint32_t)&my_fread},{"fwrite",(uint32_t)&my_fwrite},{"fgets",(uint32_t)&my_fgets},
    {"feof",(uint32_t)&my_feof},{"ferror",(uint32_t)&my_ferror},{"fflush",(uint32_t)&my_fflush},
    {"fputc",(uint32_t)&my_fputc},{"fputs",(uint32_t)&my_fputs},{"fileno",(uint32_t)&my_fileno},
    {"fdopen",(uint32_t)&my_fdopen},{"mkstemp",(uint32_t)&my_mkstemp},{"remove",(uint32_t)&my_remove},
    {"rename",(uint32_t)&my_rename},{"pipe",(uint32_t)&my_pipe},{"chmod",(uint32_t)&my_chmod},
    {"umask",(uint32_t)&my_umask},{"prctl",(uint32_t)&my_prctl},
    {"pow",(uint32_t)&my_pow},{"floor",(uint32_t)&my_floor},{"frexp",(uint32_t)&my_frexp},{"modf",(uint32_t)&my_modf},
    {"gmtime",(uint32_t)&my_gmtime},{"localtime",(uint32_t)&my_localtime},{"mktime",(uint32_t)&my_mktime},
    {"strftime",(uint32_t)&my_strftime},{"strcoll",(uint32_t)&my_strcoll},{"strxfrm",(uint32_t)&my_strxfrm},
    {"strcspn",(uint32_t)&my_strcspn},{"strspn",(uint32_t)&my_strspn},{"strpbrk",(uint32_t)&my_strpbrk},
    {"wcslen",(uint32_t)&my_wcslen},{"wmemchr",(uint32_t)&my_wmemchr},{"wmemcmp",(uint32_t)&my_wmemcmp},
    {"wmemcpy",(uint32_t)&my_wmemcpy},{"wmemmove",(uint32_t)&my_wmemmove},{"wmemset",(uint32_t)&my_wmemset},
    {"wctype",(uint32_t)&my_wctype},{"iswctype",(uint32_t)&my_iswctype},{"btowc",(uint32_t)&my_btowc},
    {"wctob",(uint32_t)&my_wctob},{"mbrtowc",(uint32_t)&my_mbrtowc},{"wcrtomb",(uint32_t)&my_wcrtomb},
    {"strerror",(uint32_t)&my_strerror},{"setvbuf",(uint32_t)&my_setvbuf},{"clearerr",(uint32_t)&my_clearerr},
    {"sigemptyset",(uint32_t)&my_sigemptyset},{"sigaddset",(uint32_t)&my_sigaddset},
    {"__longjmp_chk",(uint32_t)&my_longjmp_chk},{"_setjmp",(uint32_t)&my__setjmp},
    {"__cxa_atexit",(uint32_t)&my__cxa_atexit},{"__cxa_finalize",(uint32_t)&my__cxa_finalize},
    {"__gmon_start__",(uint32_t)&my__gmon_start__},
    {"wcscoll",(uint32_t)&my_strcoll},{"wcsftime",(uint32_t)&my_strftime},{"wcsxfrm",(uint32_t)&my_strxfrm},
    {"towlower",(uint32_t)&my_tolower},{"towupper",(uint32_t)&my_toupper},
    {"__aeabi_idiv",(uint32_t)&my_atoi},{"__aeabi_uidiv",(uint32_t)&my_atoi},
    {"__aeabi_idivmod",(uint32_t)&my_atoi},{"__aeabi_uidivmod",(uint32_t)&my_atoi},
    {"__aeabi_ldivmod",(uint32_t)&my_atoi},{"__aeabi_uldivmod",(uint32_t)&my_atoi},
    {"__aeabi_i2f",(uint32_t)&stub_ret0},{"__aeabi_ui2f",(uint32_t)&stub_ret0},
    {"__aeabi_i2d",(uint32_t)&stub_ret0},{"__aeabi_ui2d",(uint32_t)&stub_ret0},
    {"__aeabi_l2d",(uint32_t)&stub_ret0},{"__aeabi_ul2d",(uint32_t)&stub_ret0},
    {"__aeabi_f2d",(uint32_t)&stub_ret0},{"__aeabi_d2f",(uint32_t)&stub_ret0},
    {"__aeabi_d2iz",(uint32_t)&stub_ret0},{"__aeabi_d2uiz",(uint32_t)&stub_ret0},
    {"__aeabi_f2iz",(uint32_t)&stub_ret0},{"__aeabi_fadd",(uint32_t)&stub_ret0},{"__aeabi_fsub",(uint32_t)&stub_ret0},
    {"__aeabi_fmul",(uint32_t)&stub_ret0},{"__aeabi_fdiv",(uint32_t)&stub_ret0},
    {"__aeabi_dadd",(uint32_t)&stub_ret0},{"__aeabi_dsub",(uint32_t)&stub_ret0},
    {"__aeabi_dmul",(uint32_t)&stub_ret0},{"__aeabi_ddiv",(uint32_t)&stub_ret0},
    {"__aeabi_fcmpeq",(uint32_t)&stub_ret0},{"__aeabi_fcmpgt",(uint32_t)&stub_ret0},
    {"__aeabi_dcmpeq",(uint32_t)&stub_ret0},{"__aeabi_dcmpge",(uint32_t)&stub_ret0},{"__aeabi_dcmpgt",(uint32_t)&stub_ret0},
    {"__aeabi_dcmple",(uint32_t)&stub_ret0},{"__aeabi_dcmplt",(uint32_t)&stub_ret0},{"__aeabi_fcmplt",(uint32_t)&stub_ret0},
    {"_Unwind_Resume",(uint32_t)&stub_ret0},{"_Unwind_Complete",(uint32_t)&stub_ret0},
    {"_Unwind_DeleteException",(uint32_t)&stub_ret0},{"_Unwind_RaiseException",(uint32_t)&stub_ret0},
    {"_Unwind_Resume_or_Rethrow",(uint32_t)&stub_ret0},{"_Unwind_GetRegionStart",(uint32_t)&stub_ret0},
    {"_Unwind_GetDataRelBase",(uint32_t)&stub_ret0},{"_Unwind_GetTextRelBase",(uint32_t)&stub_ret0},
    {"_Unwind_GetLanguageSpecificData",(uint32_t)&stub_ret0},{"_Unwind_VRS_Get",(uint32_t)&stub_ret0},
    {"_Unwind_VRS_Set",(uint32_t)&stub_ret0},{"__gnu_unwind_frame",(uint32_t)&stub_ret0},
    {"__aeabi_unwind_cpp_pr0",(uint32_t)&stub_ret0},{"__aeabi_unwind_cpp_pr1",(uint32_t)&stub_ret0},
    {"__tls_get_addr",(uint32_t)&my_tls_get_addr},{"_Jv_RegisterClasses",(uint32_t)&stub_ret0},
    {"stderr",(uint32_t)&stub_ret0},
    {0,0}
};
static uint32_t lookup_func(const char* name){
    // strip @BLIBC... version suffix
    char nb[256]; int l0=0; while(name[l0] && name[l0]!='@' && l0<255){ nb[l0]=name[l0]; l0++; } nb[l0]=0; name=nb;
    for (int i=0; func_map[i].name; i++){ const char* a=func_map[i].name; const char* b=name; while(*a&&*a==*b){a++;b++;} if(*a==0&&*b==0) return func_map[i].addr; }
    // C++ runtime helpers returning heap pointers -> malloc-backed
    { unsigned l=0; while(name[l]) l++;
      if (my_strstr(name,"_M_create")) return (uint32_t)&my__M_create;
      if (my_strstr(name,"_Znw") || my_strstr(name,"_Zna")) return (uint32_t)&my_malloc;
      if (my_strstr(name,"_Zdl") || my_strstr(name,"_Zda") || my_strstr(name,"_M_dispose") || my_strstr(name,"_M_destroy")) return (uint32_t)&my_free; }
    return 0;
}

// ---- targets (VAs in lib, add BASE at runtime) ----
#define T_READRECT_HDR   0x6b2e0   // CMsgReader::readRectHeader(this, ?, ?, stream) — parses x,y,w,h,enc from stream
#define T_READRECT       0x68b04   // readRect body: dispatches on [this+0x158] enc (copyrect -239, -223, -311, default->decoder)
#define T_READRECT_W     0x6cd5c   // wrapper: -524 / -207 / default
#define T_HEXTILE16      0x771a0   // HextileDecoder::decode bpp16 (tile loop, mla/mul, raw subrect reads)
#define T_HEXTILE32      0x76714   // bpp32
#define T_HEXTILE8       0x76cac   // bpp8
#define T_ZRLE           0x9aa88   // ZRLEDecoder::decode
#define T_RAW            0x7eb8c   // RawDecoder::decode
#define T_RRE            0x89418   // RREDecoder::decode
#define T_TRLE           0x95f4c   // TRLEDecoder::decode
#define T_ZLIB           0x9a698   // ZlibDecoder::decode
#define T_JPEG           0x77df8   // JpegDecoder::decode
#define T_V3_FN12        0x694fc   // CMsgReaderV3 vtable fn12 (0x30) — header/msg parser w/ 288B frame
#define T_V3_FN6         0x6b0f0   // CMsgReaderV3 vtable fn6 (0x18)
#define T_V3_FN7         0x6ac0c   // CMsgReaderV3 vtable fn7 (0x1c) — calls vt[0x38]=readRect
#define T_V3_FBULOOP     0x230f4   // VNCViewerImplUNIX FBU handler (enc switch 1..20, hextile etc.)

int main(int argc, char** argv){
    if (argc < 2) raw_exit(0);
    static char buf[1<<16];
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) raw_exit(1);
    long n = read(fd, buf, sizeof(buf));
    close(fd);
    if (n < 3) raw_exit(0);
    unsigned idx = (uint8_t)buf[0] | ((uint8_t)buf[1] << 8);
    if (idx > 15) raw_exit(0);

    // ---- map lib ----
    int lfd = open(LIB_PATH, O_RDONLY);
    if (lfd < 0) raw_exit(2);
    if (mmap((void*)SEG1_VA, SEG1_FSZ, PROT_READ|PROT_EXEC|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, lfd, SEG1_OFF) == MAP_FAILED) raw_exit(3);
    if (mmap((void*)SEG2_VA, SEG2_FSZ, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, lfd, SEG2_FOFF) == MAP_FAILED) raw_exit(4);
    close(lfd);
    if (mmap((void*)(SEG2_VA+SEG2_FSZ), SEG2_END-(SEG2_VA+SEG2_FSZ), PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) raw_exit(5);
    if (mmap((void*)ARENA, ARENA_SZ, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) raw_exit(10);
    // guard pages: fb buffer is ARENA+0x20000..0x30000 (64KB); writes past it must fault
    if (mprotect((void*)(ARENA+0x30000), 0x1000, 0) != 0) { /* PROT_NONE=0 */ }
    memset((void*)(ARENA+0x80000), 0, 0x10000);  // GLOB_DAT scratch

    // ---- apply R_ARM_RELATIVE (type 23) with delta; GLOB_DAT (21) -> ARENA ----
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
            if (rtype == 23) { // R_ARM_RELATIVE: addend in place
                *(volatile uint32_t*)slot = BASE + *(volatile uint32_t*)slot;
            } else if (rtype == 21) { // GLOB_DAT: data symbol -> zeroed scratch (0x10000 bytes)
                *(volatile uint32_t*)slot = ARENA + 0x80000;
            }
        }
        for (unsigned i=0;i<N_RELPLT;i++){
            uint32_t got = relplt[i*2];
            uint32_t r_info = relplt[i*2+1];
            uint32_t sym_idx = r_info >> 8;
            const char* name = (const char*)(dynstr + dynsym[sym_idx*4]);
            uint32_t impl = lookup_func(name);
            *(volatile uint32_t*)(BASE + got) = impl ? impl : (uint32_t)&stub_ret0;
        }
    }

    // ---- input ----
    const char* payload = buf + 2;
    long plen = n - 2;
    if (plen > 60000) plen = 60000;
    if (plen < 0) plen = 0;
    memcpy(g_stream, payload, plen);
    g_stream_len = (uint32_t)plen;
    g_stream_pos = 0;

    // ---- fake objects in ARENA ----
    // stream vtable: fn[3] (0xc) = ensure, fn[8] (0x20) = read
    static struct { uint32_t pre; uint32_t vt[64]; } stream_blk;
    uint32_t* stream_vt = stream_blk.vt;
    for (int i = 0; i < 64; i++) stream_vt[i] = (uint32_t)&stub_ret0;
    // inner vtable for the [vt-4] indirection: [0]=ptr to it, [0x1c]=stream_read
    static uint32_t inner_vt[16];
    for (int i=0;i<16;i++) inner_vt[i]=(uint32_t)&stub_ret0;
    inner_vt[7] = (uint32_t)&stream_read;   // [0x1c]
    static uint32_t inner_vt2[16];
    for (int i=0;i<16;i++) inner_vt2[i]=(uint32_t)&stub_ret0;
    inner_vt2[7] = (uint32_t)&stream_read;  // [0x1c]
    inner_vt[0] = (uint32_t)inner_vt2;       // lr = inner_vt2; ip = [lr+0x1c] = stream_read
    stream_blk.pre = (uint32_t)inner_vt;     // r3 = [stream_vt-4] = inner_vt
    stream_vt[3] = (uint32_t)&stream_ensure;
    stream_vt[8] = (uint32_t)&stream_read;
    stream_vt[7] = (uint32_t)&stream_read;   // vt[0x1c] = read used by 0x1f0c7c
    // stream obj: [0]=vt, [4]=cur, [8]=end
    uint32_t stream_obj = ARENA + 0x1000;
    *(uint32_t*)(stream_obj+0) = (uint32_t)stream_vt;
    *(uint32_t*)(stream_obj+4) = (uint32_t)g_stream;       // cur
    *(uint32_t*)(stream_obj+8) = (uint32_t)(g_stream + g_stream_len); // end

    // generic stub vtable: 128 entries all -> stub_ret0
    uint32_t stub_vt = ARENA + 0x70000;
    for (int i = 0; i < 128; i++) *(uint32_t*)(stub_vt + i*4) = (uint32_t)&stub_ret0;
    // generic stub object template: 0x400 bytes, [0]=stub_vt, every ptr field -> another stub obj
    uint32_t stub_obj = ARENA + 0x71000;
    memset((void*)stub_obj, 0, 0x800);
    *(uint32_t*)(stub_obj+0) = stub_vt;
    // ptr fields -> another stub obj (zeroed, vtable=stub_vt) so [x] = 0 and vt calls -> stub_ret0
    for (unsigned off = 4; off < 0x400; off += 4) *(uint32_t*)(stub_obj+off) = (uint32_t)&stub_ret0;  // fn-ptr fields -> stub_ret0 (valid code); data derefs read mapped code bytes (harmless)
    // fake "this" CMsgReader: vtable ptr = real V3 vtable address point (BASE+0x268388)
    uint32_t this_obj = ARENA + 0x2000;
    memset((void*)this_obj, 0, 0x800);
    // pre-fill ALL pointer-ish fields with the stub object so virtual calls land on stub_ret0:
    for (unsigned off = 0x1c; off < 0x140; off += 4) {
        if (off == 0x18) continue;  // stream set below
        *(uint32_t*)(this_obj+off) = (uint32_t)&stub_ret0;
    }
    // fields >= 0x140 stay zero (counters/flags checked against 0)
    // but a few pointer fields in 0x400..0x700 are used as char*/list ptrs: point them at a zeroed byte
    // this+0x6ac is a callback obj: point the WHOLE 0x400..0x800 range at a stub object with stub_vt
    for (unsigned off = 0x400; off < 0x800; off += 4) *(uint32_t*)(this_obj+off) = ARENA + 0x72000;
    *(uint32_t*)(this_obj+0x00) = BASE + 0x268388;  // CMsgReaderV3 vtable address point
    *(uint32_t*)(this_obj+0x14) = stub_obj;      // handler/conn obj -> stub vt, zeroed fields
    *(uint32_t*)(this_obj+0x14) = ARENA + 0x72000; // dedicated handler obj
    memset((void*)(ARENA+0x72000), 0, 0x400);
    *(uint32_t*)(ARENA+0x72000) = stub_vt;
    *(uint32_t*)(this_obj+0x18) = stream_obj;      // input buffer stream
    // pixel buffer ptr field used by decoders: [this+8]? give arena buffer
    *(uint32_t*)(this_obj+0x08) = ARENA + 0x20000;  // fb buffer
    *(uint32_t*)(this_obj+0x0c) = 0;               // fb x?
    *(uint32_t*)(this_obj+0x10) = 0;
    // rect fields default 0

    // decoder "this": [0]=decoder vtable (real), [4]=conn?, [8]=fb, [0xc..0x20] tile state
    uint32_t dec_obj = ARENA + 0x3000;
    memset((void*)dec_obj, 0, 0x800);
    *(uint32_t*)(dec_obj+0x04) = 0; // per-case
    *(uint32_t*)(dec_obj+0x18) = 0;
    for (unsigned off = 0x1c; off < 0x140; off += 4) {
        if (off == 0x04 || off == 0x18) continue;  // set per-case
        *(uint32_t*)(dec_obj+off) = (uint32_t)&stub_ret0;
    }
    for (unsigned off = 0x140; off < 0x800; off += 4) *(uint32_t*)(dec_obj+off) = ARENA + 0x74000; // zeroed page
    // decoders read [dec+4] as a "buffer" object {cur,end} pair: give it the stream's cursor fields
    *(uint32_t*)(dec_obj+0x04) = stream_obj + 4;   // ptr to {cur,end} — code does ldr r0,[r5+4]; ldr r2,[r0+8]... 
    // safer: point [dec+4] directly at a struct whose +4/+8 are cur/end -> use stream_obj itself (has vt,cur,end)
    *(uint32_t*)(dec_obj+0x04) = stream_obj;

    typedef void (*fn1_t)(void*);
    typedef void (*fn4_t)(void*, void*, void*, void*);
    typedef void (*fn5_t)(void*, void*, void*, void*, void*);
    typedef void (*fn3_t)(void*, void*, void*);

    switch (idx) {
    case 0: // readRectHeader(this, 0, 0, stream)
        ((fn5_t)(BASE+T_READRECT_HDR))((void*)this_obj, (void*)0, (void*)0, (void*)stream_obj, (void*)stream_obj);
        break;
    case 1: // readRect with enc pre-set from first 4 payload bytes (BE s32)
        if (plen >= 4) *(uint32_t*)(this_obj+0x158) = ((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3];
        *(uint32_t*)(this_obj+0x148) = 0; *(uint32_t*)(this_obj+0x14c) = 0;
        *(uint32_t*)(this_obj+0x150) = 16; *(uint32_t*)(this_obj+0x154) = 16; // w,h via right/bottom edges
        g_stream_pos = 4;
        ((fn5_t)(BASE+T_READRECT))((void*)this_obj, (void*)stream_obj, (void*)stream_obj, (void*)0, (void*)stream_obj);
        break;
    case 2: // wrapper 0x6cd5c (r2 = enc from payload[0..3])
        {
            uint32_t enc = 0;
            if (plen >= 4) enc = ((uint8_t)payload[0]<<24)|((uint8_t)payload[1]<<16)|((uint8_t)payload[2]<<8)|(uint8_t)payload[3];
            g_stream_pos = 4;
            typedef void (*fn3e_t)(void*, void*, uint32_t);
            ((fn5_t)(BASE+T_READRECT_W))((void*)this_obj, (void*)0, (void*)(uintptr_t)enc, (void*)stream_obj, (void*)stream_obj);
        }
        break;
    case 3: case 4: case 5: { // hextile decoders bpp16/32/8: (this=dec, r1=rect/stream?, r2=?, r3=bpp?)
        uint32_t vt = idx==3 ? 0x268930 : idx==4 ? 0x268e60 : 0x268930;
        // use matching vtable: hextile vtable addr point 0x268930 (all bpp share class? no — use HextileDecoder vt)
        *(uint32_t*)(dec_obj+0x00) = BASE + 0x268930; // HextileDecoder vtable
        *(uint32_t*)(dec_obj+0x04) = stream_obj;
        *(uint32_t*)(dec_obj+0x18) = stream_obj;
        *(uint32_t*)(dec_obj+0x08) = ARENA + 0x20000;  // pixel buffer
        *(uint32_t*)(dec_obj+0x0c) = 0; *(uint32_t*)(dec_obj+0x10) = 0;
        *(uint32_t*)(dec_obj+0x14) = 16; *(uint32_t*)(dec_obj+0x18) = 16;
        uint32_t fn = idx==3 ? T_HEXTILE16 : idx==4 ? T_HEXTILE32 : T_HEXTILE8;
        ((fn5_t)(BASE+fn))((void*)dec_obj, (void*)stream_obj, (void*)stream_obj, (void*)(uintptr_t)(idx==3?16:idx==4?32:8), (void*)stream_obj);
        break;
    }
    case 6: { *(uint32_t*)(dec_obj+0x00)=BASE+0x268fd0; *(uint32_t*)(dec_obj+0x04)=stream_obj; *(uint32_t*)(dec_obj+0x18)=stream_obj; *(uint32_t*)(dec_obj+0x2c)=stream_obj; ((fn5_t)(BASE+T_ZRLE))((void*)dec_obj,(void*)stream_obj,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 7: { *(uint32_t*)(dec_obj+0x00)=BASE+0x268bb8; *(uint32_t*)(dec_obj+0x04)=stream_obj; *(uint32_t*)(dec_obj+0x18)=stream_obj; ((fn5_t)(BASE+T_RAW))((void*)dec_obj,(void*)stream_obj,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 8: { *(uint32_t*)(dec_obj+0x00)=BASE+0x268bf8; *(uint32_t*)(dec_obj+0x04)=stream_obj; *(uint32_t*)(dec_obj+0x18)=stream_obj; ((fn5_t)(BASE+T_RRE))((void*)dec_obj,(void*)stream_obj,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 9: { *(uint32_t*)(dec_obj+0x00)=BASE+0x268e60; *(uint32_t*)(dec_obj+0x04)=stream_obj; *(uint32_t*)(dec_obj+0x18)=stream_obj; ((fn5_t)(BASE+T_TRLE))((void*)dec_obj,(void*)stream_obj,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 10:{ *(uint32_t*)(dec_obj+0x00)=BASE+0x268f90; *(uint32_t*)(dec_obj+0x04)=stream_obj; *(uint32_t*)(dec_obj+0x18)=stream_obj; ((fn5_t)(BASE+T_ZLIB))((void*)dec_obj,(void*)stream_obj,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 11:{ *(uint32_t*)(dec_obj+0x00)=BASE+0x268980; *(uint32_t*)(dec_obj+0x04)=stream_obj; *(uint32_t*)(dec_obj+0x18)=stream_obj; ((fn5_t)(BASE+T_JPEG))((void*)dec_obj,(void*)stream_obj,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 12:{ ((fn5_t)(BASE+T_V3_FN12))((void*)this_obj,(void*)(ARENA+0x4000),(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 13:{ ((fn5_t)(BASE+T_V3_FN6))((void*)this_obj,(void*)(ARENA+0x4000),(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 14:{ ((fn5_t)(BASE+T_V3_FN7))((void*)this_obj,(void*)(ARENA+0x4000),(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    case 15:{ uint32_t emptylist = ARENA + 0x73000; memset((void*)emptylist, 0, 0x400); ((fn5_t)(BASE+T_V3_FBULOOP))((void*)this_obj,(void*)emptylist,(void*)stream_obj,(void*)0,(void*)stream_obj); break; }
    }
    raw_exit(0);
    return 0;
}
