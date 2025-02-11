/* This file was generated by the Hex-Rays decompiler version 8.0.0.220729.
   Copyright (c) 2007-2021 Hex-Rays <info@hex-rays.com>

   Detected compiler: GNU C++
*/

#include <defs.h>


//-------------------------------------------------------------------------
// Function declarations

int emit_stdin_note();
int emit_mandatory_arg_note();
unsigned long  emit_ancillary_info(const char *a1);
void   usage(int a1);
int  main(int argc, const char **argv, const char **envp);
signed long  set_prefix(char *a1);
long  fmt(struct _IO_FILE *a1, long a2);
long  set_other_indent(char a1);
long  get_paragraph(FILE *a1);
long  copy_rest(FILE *a1, unsigned int a2);
_BOOL8  same_para(int a1);
long  get_line(FILE *a1, char a2);
long  get_prefix(FILE *a1);
long  get_space(FILE *a1, int a2);
char ** check_punctuation(unsigned long *a1);
char *flush_paragraph();
long fmt_paragraph();
long  base_cost(unsigned long a1);
long  line_cost(long a1, int a2);
long  put_paragraph(long a1);
int  put_line(long a1, int a2);
long  put_word(char **a1);
long  put_space(int a1);
// char *gettext(const char *msgid);
// int fputs_unlocked(const char *s, FILE *stream);
// int strcmp(const char *s1, const char *s2);
// int printf(const char *format, ...);
// char *setlocale(int category, const char *locale);
// int strncmp(const char *s1, const char *s2, size_t n);
// int fprintf(FILE *stream, const char *format, ...);
// void  exit(int status);
// long  set_program_name(_QWORD, _QWORD, _QWORD); weak
// char *bindtextdomain(const char *domainname, const char *dirname);
// char *textdomain(const char *domainname);
// int atexit(void (*func)(void));
// void error(int status, int errnum, const char *format, ...);
// long  version_etc(_QWORD, _QWORD, _QWORD, _QWORD, _QWORD, _QWORD); weak
// int getopt_long(int argc, char *const *argv, const char *shortopts, const struct option *longopts, int *longind);
// long  xdectoumax(_QWORD, _QWORD, _QWORD, _QWORD, _QWORD, _QWORD); weak
// FILE *fopen(const char *filename, const char *modes);
// long  quotearg_style(_QWORD, _QWORD); weak
// int *_errno_location(void);
// long  rpl_fclose(_QWORD); weak
// size_t strlen(const char *s);
// long  fadvise(_QWORD, _QWORD); weak
// int ferror_unlocked(FILE *stream);
// void clearerr_unlocked(FILE *stream);
// long  quotearg_n_style_colon(_QWORD, _QWORD, _QWORD); weak
// int putchar_unlocked(int c);
// void  _assert_fail(const char *assertion, const char *file, unsigned int line, const char *function);
// int getc_unlocked(FILE *stream);
// long  c_isspace(_QWORD); weak
// char *strchr(const char *s, int c);
// const unsigned short **_ctype_b_loc(void);
// size_t fwrite_unlocked(const void *ptr, size_t size, size_t n, FILE *stream);
// void *memmove(void *dest, const void *src, size_t n);

//-------------------------------------------------------------------------
// Data declarations

char crown; // weak
char tagged; // weak
char split; // weak
char uniform; // weak
char *prefix; // idb
int max_width; // weak
int prefix_full_length; // weak
int prefix_lead_space; // weak
int prefix_length; // weak
int goal_width; // weak
int in_column; // weak
int out_column; // weak
_UNKNOWN parabuf; // weak
long wptr; // weak
_UNKNOWN unused_word_type; // weak
long qword_2F40; // weak
_UNKNOWN unk_2F48; // weak
_UNKNOWN unk_CB10; // weak
long word_limit; // weak
char tabs; // weak
int prefix_indent; // weak
int first_indent; // weak
int other_indent; // weak
int next_char; // weak
int next_prefix_indent; // weak
int last_line_length; // weak
const char locale[5] = { '\0', '\0', '\0', '\0', '\0' }; // idb
struct option long_options = { "crown-margin", 0, &emit_stdin_note, 99 }; // idb
// extern struct _IO_FILE *stdout;
// extern _UNKNOWN program_name; weak
// extern struct _IO_FILE *stderr;
// extern void (*close_stdout)(void); weak
// extern char *optarg;
// extern _UNKNOWN Version; weak
// extern int optind;
// extern struct _IO_FILE *stdin;


//----- (0000000000000000) ----------------------------------------------------
int emit_stdin_note()
{
  FILE *v0; // rbx
  char *v1; // rax

  v0 = stdout;
  v1 = gettext("\nWith no FILE, or when FILE is -, read standard input.\n");
  return fputs_unlocked(v1, v0);
}

//----- (000000000000002F) ----------------------------------------------------
int emit_mandatory_arg_note()
{
  FILE *v0; // rbx
  char *v1; // rax

  v0 = stdout;
  v1 = gettext("\nMandatory arguments to long options are mandatory for short options too.\n");
  return fputs_unlocked(v1, v0);
}

//----- (000000000000005E) ----------------------------------------------------
unsigned long  emit_ancillary_info(const char *a1)
{
  char *v1; // rax
  FILE *v2; // rbx
  char *v3; // rax
  const char *v4; // rax
  char *v5; // rax
  const char *v6; // rbx
  char *v7; // rax
  const char *v9; // [rsp+10h] [rbp-B0h]
  long *i; // [rsp+18h] [rbp-A8h]
  const char *v11; // [rsp+20h] [rbp-A0h]
  const char *v12; // [rsp+28h] [rbp-98h]
  long v13[15]; // [rsp+30h] [rbp-90h] BYREF
  unsigned long v14; // [rsp+A8h] [rbp-18h]

  v14 = __readfsqword(0x28u);
  v13[0] = (long)"[";
  v13[1] = (long)"test invocation";
  v13[2] = (long)"coreutils";
  v13[3] = (long)"Multi-call invocation";
  v13[4] = (long)"sha224sum";
  v13[5] = (long)"sha2 utilities";
  v13[6] = (long)"sha256sum";
  v13[7] = (long)"sha2 utilities";
  v13[8] = (long)"sha384sum";
  v13[9] = (long)"sha2 utilities";
  v13[10] = (long)"sha512sum";
  v13[11] = (long)"sha2 utilities";
  v13[12] = 0LL;
  v13[13] = 0LL;
  v9 = a1;
  for ( i = v13; *i && strcmp(a1, (const char *)*i); i += 2 )
    ;
  if ( i[1] )
    v9 = (const char *)i[1];
  v1 = gettext("\n%s online help: <%s>\n");
  printf(v1, "GNU coreutils", "https://www.gnu.org/software/coreutils/");
  v11 = setlocale(5, 0LL);
  if ( v11 && strncmp(v11, "en_", 3uLL) )
  {
    v2 = stdout;
    v3 = gettext("Report any translation bugs to <https://translationproject.org/team/>\n");
    fputs_unlocked(v3, v2);
  }
  if ( !strcmp(a1, "[") )
    v4 = "test";
  else
    v4 = a1;
  v12 = v4;
  v5 = gettext("Full documentation <%s%s>\n");
  printf(v5, "https://www.gnu.org/software/coreutils/", v12);
  if ( v9 == a1 )
    v6 = " invocation";
  else
    v6 = locale;
  v7 = gettext("or available locally via: info '(coreutils) %s%s'\n");
  printf(v7, v9, v6);
  return __readfsqword(0x28u) ^ v14;
}

//----- (00000000000002DB) ----------------------------------------------------
void   usage(int a1)
{
  long v1; // rbx
  char *v2; // rax
  char *v3; // rax
  FILE *v4; // rbx
  char *v5; // rax
  FILE *v6; // rbx
  char *v7; // rax
  FILE *v8; // rbx
  char *v9; // rax
  FILE *v10; // rbx
  char *v11; // rax
  FILE *v12; // rbx
  char *v13; // rax

  v1 = program_name;
  if ( a1 )
  {
    v2 = gettext("Try '%s --help' for more information.\n");
    fprintf(stderr, v2, v1);
  }
  else
  {
    v3 = gettext("Usage: %s [-WIDTH] [OPTION]... [FILE]...\n");
    printf(v3, v1);
    v4 = stdout;
    v5 = gettext(
           "Reformat each paragraph in the FILE(s), writing to standard output.\n"
           "The option -WIDTH is an abbreviated form of --width=DIGITS.\n");
    fputs_unlocked(v5, v4);
    emit_stdin_note();
    emit_mandatory_arg_note();
    v6 = stdout;
    v7 = gettext(
           "  -c, --crown-margin        preserve indentation of first two lines\n"
           "  -p, --prefix=STRING       reformat only lines beginning with STRING,\n"
           "                              reattaching the prefix to reformatted lines\n"
           "  -s, --split-only          split long lines, but do not refill\n");
    fputs_unlocked(v7, v6);
    v8 = stdout;
    v9 = gettext(
           "  -t, --tagged-paragraph    indentation of first line different from second\n"
           "  -u, --uniform-spacing     one space between words, two after sentences\n"
           "  -w, --width=WIDTH         maximum line width (default of 75 columns)\n"
           "  -g, --goal=WIDTH          goal width (default of 93% of width)\n");
    fputs_unlocked(v9, v8);
    v10 = stdout;
    v11 = gettext("      --help        display this help and exit\n");
    fputs_unlocked(v11, v10);
    v12 = stdout;
    v13 = gettext("      --version     output version information and exit\n");
    fputs_unlocked(v13, v12);
    emit_ancillary_info("fmt");
  }
  exit(a1);
}

//----- (00000000000003FF) ----------------------------------------------------
int  main(int argc, const char **argv, const char **envp)
{
  char *v3; // rax
  char *v4; // rdx
  char *v5; // rcx
  long v6; // r12
  char *v7; // rbx
  int *v8; // rax
  char *v9; // rbx
  int *v10; // rax
  char **argva; // [rsp+0h] [rbp-50h]
  int argca; // [rsp+Ch] [rbp-44h]
  char v14; // [rsp+1Ah] [rbp-36h]
  char v15; // [rsp+1Bh] [rbp-35h]
  int v16; // [rsp+1Ch] [rbp-34h]
  char *v17; // [rsp+20h] [rbp-30h]
  char *v18; // [rsp+28h] [rbp-28h]
  char *s1; // [rsp+30h] [rbp-20h]
  FILE *v20; // [rsp+38h] [rbp-18h]

  argca = argc;
  argva = (char **)argv;
  v14 = 1;
  v17 = 0LL;
  v18 = 0LL;
  set_program_name(*argv, argv, envp);
  setlocale(6, locale);
  bindtextdomain("coreutils", "/usr/local/share/locale");
  textdomain("coreutils");
  atexit((void (*)(void))&close_stdout);
  uniform = 0;
  split = 0;
  tagged = 0;
  crown = 0;
  max_width = 75;
  prefix = (char *)locale;
  prefix_full_length = 0;
  prefix_lead_space = 0;
  prefix_length = 0;
  if ( argc > 1 && *argv[1] == 45 && (unsigned int)(argv[1][1] - 48) <= 9 )
  {
    v17 = (char *)(argv[1] + 1);
    argv[1] = *argv;
    argva = (char **)(argv + 1);
    argca = argc - 1;
  }
  while ( 2 )
  {
    v16 = getopt_long(argca, argva, "0123456789cstuw:p:g:", &long_options, 0LL);
    if ( v16 != -1 )
    {
      if ( v16 <= 119 )
      {
        if ( v16 >= 99 )
        {
          switch ( v16 )
          {
            case 'c':
              crown = 1;
              continue;
            case 'g':
              v18 = optarg;
              continue;
            case 'p':
              set_prefix(optarg);
              continue;
            case 's':
              split = 1;
              continue;
            case 't':
              tagged = 1;
              continue;
            case 'u':
              uniform = 1;
              continue;
            case 'w':
              v17 = optarg;
              continue;
            default:
              goto LABEL_11;
          }
        }
        if ( v16 == -131 )
        {
          version_etc(stdout, "fmt", "GNU coreutils", Version, "Ross Paterson", 0LL);
          exit(0);
        }
        if ( v16 == -130 )
          usage(0);
      }
LABEL_11:
      if ( (unsigned int)(v16 - 48) <= 9 )
      {
        v3 = gettext("invalid option -- %c; -WIDTH is recognized only when it is the first\noption; use -w N instead");
        error(0, 0, v3, (unsigned int)v16);
      }
      usage(1);
    }
    break;
  }
  if ( v17 )
  {
    v4 = gettext("invalid width");
    max_width = xdectoumax(v17, 0LL, 2500LL, locale, v4, 0LL);
  }
  if ( v18 )
  {
    v5 = gettext("invalid width");
    goal_width = xdectoumax(v18, 0LL, max_width, locale, v5, 0LL);
    if ( !v17 )
      max_width = goal_width + 10;
  }
  else
  {
    goal_width = 187 * max_width / 200;
  }
  v15 = 0;
  if ( argca == optind )
  {
    v15 = 1;
    v14 = fmt(stdin, (long)"-");
  }
  else
  {
    while ( argca > optind )
    {
      s1 = argva[optind];
      if ( !strcmp(s1, "-") )
      {
        v14 = (unsigned char)(v14 & fmt(stdin, (long)s1)) != 0;
        v15 = 1;
      }
      else
      {
        v20 = fopen(s1, "r");
        if ( v20 )
        {
          v14 = (unsigned char)(v14 & fmt(v20, (long)s1)) != 0;
        }
        else
        {
          v6 = quotearg_style(4LL, s1);
          v7 = gettext("cannot open %s for reading");
          v8 = _errno_location();
          error(0, *v8, v7, v6);
          v14 = 0;
        }
      }
      ++optind;
    }
  }
  if ( v15 && (unsigned int)rpl_fclose(stdin) )
  {
    v9 = gettext("closing standard input");
    v10 = _errno_location();
    error(1, *v10, "%s", v9);
  }
  return (unsigned char)v14 ^ 1;
}
// 1B40: using guessed type char crown;
// 1B41: using guessed type char tagged;
// 1B42: using guessed type char split;
// 1B43: using guessed type char uniform;
// 1B50: using guessed type int max_width;
// 1B54: using guessed type int prefix_full_length;
// 1B58: using guessed type int prefix_lead_space;
// 1B5C: using guessed type int prefix_length;
// 1B60: using guessed type int goal_width;
// D780: using guessed type long  set_program_name(_QWORD, _QWORD, _QWORD);
// D798: using guessed type void (*close_stdout)(void);
// D7C0: using guessed type long  version_etc(_QWORD, _QWORD, _QWORD, _QWORD, _QWORD, _QWORD);
// D7D0: using guessed type long  xdectoumax(_QWORD, _QWORD, _QWORD, _QWORD, _QWORD, _QWORD);
// D7F0: using guessed type long  quotearg_style(_QWORD, _QWORD);
// D800: using guessed type long  rpl_fclose(_QWORD);

//----- (0000000000000922) ----------------------------------------------------
signed long  set_prefix(char *a1)
{
  signed long result; // rax
  char *i; // [rsp+18h] [rbp-8h]

  prefix_lead_space = 0;
  while ( *a1 == 32 )
  {
    ++prefix_lead_space;
    ++a1;
  }
  prefix = a1;
  prefix_full_length = strlen(a1);
  for ( i = &a1[prefix_full_length]; i > a1 && *(i - 1) == 32; --i )
    ;
  *i = 0;
  result = i - a1;
  prefix_length = (_DWORD)i - (_DWORD)a1;
  return result;
}
// 1B54: using guessed type int prefix_full_length;
// 1B58: using guessed type int prefix_lead_space;
// 1B5C: using guessed type int prefix_length;

//----- (00000000000009C6) ----------------------------------------------------
long  fmt(struct _IO_FILE *a1, long a2)
{
  int v2; // eax
  long v3; // rbx
  char *v4; // rax
  int errnum; // [rsp+1Ch] [rbp-14h]

  fadvise(a1, 2LL);
  tabs = 0;
  other_indent = 0;
  next_char = get_prefix(a1);
  while ( (unsigned char)get_paragraph(a1) )
  {
    fmt_paragraph();
    put_paragraph(word_limit);
  }
  if ( ferror_unlocked(a1) )
    v2 = 0;
  else
    v2 = -1;
  errnum = v2;
  if ( a1 == stdin )
  {
    clearerr_unlocked(a1);
  }
  else if ( (unsigned int)rpl_fclose(a1) && errnum < 0 )
  {
    errnum = *_errno_location();
  }
  if ( errnum >= 0 )
  {
    v3 = quotearg_n_style_colon(0LL, 3LL, a2);
    if ( errnum )
      v4 = "%s";
    else
      v4 = gettext("read error");
    error(0, errnum, v4, v3);
  }
  return (unsigned int)errnum >> 31;
}
// CB60: using guessed type long word_limit;
// CB68: using guessed type char tabs;
// CB74: using guessed type int other_indent;
// CB78: using guessed type int next_char;
// D800: using guessed type long  rpl_fclose(_QWORD);
// D810: using guessed type long  fadvise(_QWORD, _QWORD);
// D828: using guessed type long  quotearg_n_style_colon(_QWORD, _QWORD, _QWORD);

//----- (0000000000000AEE) ----------------------------------------------------
long  set_other_indent(char a1)
{
  long result; // rax

  if ( split )
  {
    result = (unsigned int)first_indent;
    other_indent = first_indent;
  }
  else if ( crown )
  {
    if ( a1 )
      result = (unsigned int)in_column;
    else
      result = (unsigned int)first_indent;
    other_indent = result;
  }
  else if ( tagged )
  {
    if ( !a1 || in_column == first_indent )
    {
      result = (unsigned int)first_indent;
      if ( other_indent == first_indent )
      {
        if ( first_indent )
          result = 0LL;
        else
          result = 3LL;
        other_indent = result;
      }
    }
    else
    {
      result = (unsigned int)in_column;
      other_indent = in_column;
    }
  }
  else
  {
    result = (unsigned int)first_indent;
    other_indent = first_indent;
  }
  return result;
}
// 1B40: using guessed type char crown;
// 1B41: using guessed type char tagged;
// 1B42: using guessed type char split;
// 1B64: using guessed type int in_column;
// CB70: using guessed type int first_indent;
// CB74: using guessed type int other_indent;

//----- (0000000000000BAA) ----------------------------------------------------
long  get_paragraph(FILE *a1)
{
  bool v2; // al
  long v3; // rax
  int i; // [rsp+1Ch] [rbp-4h]
  int line; // [rsp+1Ch] [rbp-4h]

  last_line_length = 0;
  for ( i = next_char;
        i == 10
     || i == -1
     || next_prefix_indent < prefix_lead_space
     || prefix_full_length + next_prefix_indent > in_column;
        i = get_prefix(a1) )
  {
    if ( (unsigned int)copy_rest(a1, i) == -1 )
    {
      next_char = -1;
      return 0LL;
    }
    putchar_unlocked(10);
  }
  prefix_indent = next_prefix_indent;
  first_indent = in_column;
  wptr = (long)&parabuf;
  word_limit = (long)&unused_word_type;
  line = get_line(a1, i);
  v2 = same_para(line);
  set_other_indent(v2);
  if ( !split )
  {
    if ( crown )
    {
      if ( same_para(line) )
      {
        do
          line = get_line(a1, line);
        while ( same_para(line) && in_column == other_indent );
      }
    }
    else if ( tagged )
    {
      if ( same_para(line) && in_column != first_indent )
      {
        do
          line = get_line(a1, line);
        while ( same_para(line) && in_column == other_indent );
      }
    }
    else
    {
      while ( same_para(line) && in_column == other_indent )
        line = get_line(a1, line);
    }
  }
  if ( word_limit <= (unsigned long)&unused_word_type )
    _assert_fail("word < word_limit", "src/fmt.c", 0x270u, "get_paragraph");
  v3 = word_limit - 40;
  *(_BYTE *)(v3 + 16) = *(_BYTE *)(word_limit - 40 + 16) | 8;
  *(_BYTE *)(word_limit - 40 + 16) = (2 * ((*(_BYTE *)(v3 + 16) & 8) != 0)) | *(_BYTE *)(word_limit - 40 + 16) & 0xFD;
  next_char = line;
  return 1LL;
}
// 1B40: using guessed type char crown;
// 1B41: using guessed type char tagged;
// 1B42: using guessed type char split;
// 1B54: using guessed type int prefix_full_length;
// 1B58: using guessed type int prefix_lead_space;
// 1B64: using guessed type int in_column;
// 2F08: using guessed type long wptr;
// CB60: using guessed type long word_limit;
// CB6C: using guessed type int prefix_indent;
// CB70: using guessed type int first_indent;
// CB74: using guessed type int other_indent;
// CB78: using guessed type int next_char;
// CB7C: using guessed type int next_prefix_indent;
// CB80: using guessed type int last_line_length;

//----- (0000000000000E1A) ----------------------------------------------------
long  copy_rest(FILE *a1, unsigned int a2)
{
  char *v2; // rax
  unsigned int c; // [rsp+4h] [rbp-1Ch]
  char *i; // [rsp+18h] [rbp-8h]

  c = a2;
  out_column = 0;
  if ( in_column > next_prefix_indent || a2 != 10 && a2 != -1 )
  {
    put_space(next_prefix_indent);
    for ( i = prefix; out_column != in_column && *i; ++i )
    {
      v2 = i;
      putchar_unlocked(*v2);
      ++out_column;
    }
    if ( a2 != -1 && a2 != 10 )
      put_space(in_column - out_column);
    if ( a2 == -1 && prefix_length + next_prefix_indent <= in_column )
      putchar_unlocked(10);
  }
  while ( c != 10 && c != -1 )
  {
    putchar_unlocked(c);
    c = getc_unlocked(a1);
  }
  return c;
}
// 1B5C: using guessed type int prefix_length;
// 1B64: using guessed type int in_column;
// 1B68: using guessed type int out_column;
// CB7C: using guessed type int next_prefix_indent;

//----- (0000000000000F2F) ----------------------------------------------------
_BOOL8  same_para(int a1)
{
  return next_prefix_indent == prefix_indent
      && prefix_full_length + next_prefix_indent <= in_column
      && a1 != 10
      && a1 != -1;
}
// 1B54: using guessed type int prefix_full_length;
// 1B64: using guessed type int in_column;
// CB6C: using guessed type int prefix_indent;
// CB7C: using guessed type int next_prefix_indent;

//----- (0000000000000F7F) ----------------------------------------------------
long  get_line(FILE *a1, char a2)
{
  _BYTE *v2; // rax
  long v3; // rax
  bool v4; // al
  int v5; // edx
  unsigned int space; // [rsp+4h] [rbp-2Ch]
  int v8; // [rsp+1Ch] [rbp-14h]

  LOBYTE(space) = a2;
  do
  {
    *(_QWORD *)word_limit = wptr;
    do
    {
      if ( &wptr == (long *)wptr )
      {
        set_other_indent(1);
        flush_paragraph();
      }
      v2 = (_BYTE *)wptr++;
      *v2 = space;
      space = getc_unlocked(a1);
    }
    while ( space != -1 && (unsigned char)c_isspace(space) != 1 );
    v3 = word_limit;
    *(_DWORD *)(word_limit + 8) = wptr - *(_QWORD *)word_limit;
    in_column += *(_DWORD *)(v3 + 8);
    check_punctuation((unsigned long *)word_limit);
    v8 = in_column;
    space = get_space(a1, space);
    *(_DWORD *)(word_limit + 12) = in_column - v8;
    v4 = space == -1 || (*(_BYTE *)(word_limit + 16) & 2) != 0 && (space == 10 || *(int *)(word_limit + 12) > 1);
    *(_BYTE *)(word_limit + 16) = (8 * v4) | *(_BYTE *)(word_limit + 16) & 0xF7;
    if ( space == 10 || space == -1 || uniform )
    {
      if ( (*(_BYTE *)(word_limit + 16) & 8) != 0 )
        v5 = 2;
      else
        v5 = 1;
      *(_DWORD *)(word_limit + 12) = v5;
    }
    if ( &unk_CB10 == (_UNKNOWN *)word_limit )
    {
      set_other_indent(1);
      flush_paragraph();
    }
    word_limit += 40LL;
  }
  while ( space != 10 && space != -1 );
  return get_prefix(a1);
}
// 1B43: using guessed type char uniform;
// 1B64: using guessed type int in_column;
// 2F08: using guessed type long wptr;
// CB60: using guessed type long word_limit;
// D848: using guessed type long  c_isspace(_QWORD);

//----- (0000000000001164) ----------------------------------------------------
long  get_prefix(FILE *a1)
{
  int v1; // eax
  int v2; // eax
  unsigned int space; // [rsp+14h] [rbp-Ch]
  char *i; // [rsp+18h] [rbp-8h]

  in_column = 0;
  v1 = getc_unlocked(a1);
  space = get_space(a1, v1);
  if ( prefix_length )
  {
    next_prefix_indent = in_column;
    for ( i = prefix; *i; ++i )
    {
      if ( space != (unsigned char)*i )
        return space;
      ++in_column;
      space = getc_unlocked(a1);
    }
    return (unsigned int)get_space(a1, space);
  }
  else
  {
    v2 = prefix_lead_space;
    if ( in_column <= prefix_lead_space )
      v2 = in_column;
    next_prefix_indent = v2;
  }
  return space;
}
// 1B58: using guessed type int prefix_lead_space;
// 1B5C: using guessed type int prefix_length;
// 1B64: using guessed type int in_column;
// CB7C: using guessed type int next_prefix_indent;

//----- (0000000000001238) ----------------------------------------------------
long  get_space(FILE *a1, int a2)
{
  while ( 1 )
  {
    if ( a2 == 32 )
    {
      ++in_column;
      goto LABEL_6;
    }
    if ( a2 != 9 )
      return (unsigned int)a2;
    tabs = 1;
    in_column = 8 * (in_column / 8 + 1);
LABEL_6:
    a2 = getc_unlocked(a1);
  }
}
// 1B64: using guessed type int in_column;
// CB68: using guessed type char tabs;

//----- (00000000000012A6) ----------------------------------------------------
char ** check_punctuation(unsigned long *a1)
{
  bool v1; // dl
  char **result; // rax
  unsigned char v3; // [rsp+1Fh] [rbp-11h]
  char *v4; // [rsp+20h] [rbp-10h]
  unsigned long v5; // [rsp+28h] [rbp-8h]

  v5 = *a1;
  v4 = (char *)(*((int *)a1 + 2) - 1LL + *a1);
  v3 = *v4;
  *((_BYTE *)a1 + 16) = (strchr("(['`\"", *(char *)*a1) != 0LL) | a1[2] & 0xFE;
  *((_BYTE *)a1 + 16) = (4 * (((*_ctype_b_loc())[v3] & 4) != 0)) | a1[2] & 0xFB;
  while ( v5 < (unsigned long)v4 && strchr(")]'\"", *v4) )
    --v4;
  v1 = strchr(".?!", *v4) != 0LL;
  result = (char **)a1;
  *((_BYTE *)a1 + 16) = (2 * v1) | a1[2] & 0xFD;
  return result;
}

//----- (00000000000013B5) ----------------------------------------------------
char *flush_paragraph()
{
  char *result; // rax
  signed int v1; // [rsp+4h] [rbp-1Ch]
  const void **src; // [rsp+8h] [rbp-18h]
  long i; // [rsp+10h] [rbp-10h]
  const void **j; // [rsp+10h] [rbp-10h]
  long v5; // [rsp+18h] [rbp-8h]

  if ( (_UNKNOWN *)word_limit == &unused_word_type )
  {
    fwrite_unlocked(&parabuf, 1uLL, wptr - (_QWORD)&parabuf, stdout);
    result = (char *)&parabuf;
    wptr = (long)&parabuf;
  }
  else
  {
    fmt_paragraph();
    src = (const void **)word_limit;
    v5 = 0x7FFFFFFFFFFFFFFFLL;
    for ( i = qword_2F40; i != word_limit; i = *(_QWORD *)(i + 32) )
    {
      if ( v5 > *(_QWORD *)(i + 24) - *(_QWORD *)(*(_QWORD *)(i + 32) + 24LL) )
      {
        src = (const void **)i;
        v5 = *(_QWORD *)(i + 24) - *(_QWORD *)(*(_QWORD *)(i + 32) + 24LL);
      }
      if ( v5 <= 0x7FFFFFFFFFFFFFF6LL )
        v5 += 9LL;
    }
    put_paragraph((long)src);
    memmove(&parabuf, *src, wptr - (_QWORD)*src);
    v1 = (unsigned int)*src - (unsigned int)&parabuf;
    wptr -= v1;
    for ( j = src; (unsigned long)j <= word_limit; j += 5 )
      *j = (char *)*j - v1;
    memmove(&unused_word_type, src, word_limit - (_QWORD)src + 40);
    result = (char *)(&unused_word_type - (_UNKNOWN *)src + word_limit);
    word_limit = (long)result;
  }
  return result;
}
// 2F08: using guessed type long wptr;
// 2F40: using guessed type long qword_2F40;
// CB60: using guessed type long word_limit;

//----- (0000000000001595) ----------------------------------------------------
long fmt_paragraph()
{
  int v0; // eax
  long result; // rax
  int v2; // [rsp+8h] [rbp-28h]
  int v3; // [rsp+Ch] [rbp-24h]
  unsigned long i; // [rsp+10h] [rbp-20h]
  long v5; // [rsp+18h] [rbp-18h]
  long v6; // [rsp+20h] [rbp-10h]
  long v7; // [rsp+28h] [rbp-8h]

  *(_QWORD *)(word_limit + 24) = 0LL;
  v3 = *(_DWORD *)(word_limit + 8);
  *(_DWORD *)(word_limit + 8) = max_width;
  for ( i = word_limit - 40; i >= (unsigned long)&unused_word_type; i -= 40LL )
  {
    v7 = 0x7FFFFFFFFFFFFFFFLL;
    if ( (_UNKNOWN *)i == &unused_word_type )
      v0 = first_indent;
    else
      v0 = other_indent;
    v5 = i;
    v2 = *(_DWORD *)(i + 8) + v0;
    do
    {
      v5 += 40LL;
      v6 = *(_QWORD *)(v5 + 24) + line_cost(v5, v2);
      if ( (_UNKNOWN *)i == &unused_word_type && last_line_length > 0 )
        v6 += 10 * (v2 - last_line_length) * (long)(10 * (v2 - last_line_length)) / 2;
      if ( v6 < v7 )
      {
        v7 = v6;
        *(_QWORD *)(i + 32) = v5;
        *(_DWORD *)(i + 20) = v2;
      }
      if ( v5 == word_limit )
        break;
      v2 += *(_DWORD *)(v5 - 40 + 12) + *(_DWORD *)(v5 + 8);
    }
    while ( v2 < max_width );
    *(_QWORD *)(i + 24) = base_cost(i) + v7;
  }
  result = word_limit;
  *(_DWORD *)(word_limit + 8) = v3;
  return result;
}
// 1B50: using guessed type int max_width;
// CB60: using guessed type long word_limit;
// CB70: using guessed type int first_indent;
// CB74: using guessed type int other_indent;
// CB80: using guessed type int last_line_length;

//----- (000000000000173C) ----------------------------------------------------
long  base_cost(unsigned long a1)
{
  long v2; // [rsp+10h] [rbp-8h]

  v2 = 4900LL;
  if ( a1 > (unsigned long)&unused_word_type )
  {
    if ( (*(_BYTE *)(a1 - 40 + 16) & 2) != 0 )
    {
      if ( (*(_BYTE *)(a1 - 40 + 16) & 8) != 0 )
        v2 = 2400LL;
      else
        v2 = 364900LL;
    }
    else if ( (*(_BYTE *)(a1 - 40 + 16) & 4) != 0 )
    {
      v2 = 3300LL;
    }
    else if ( a1 > (unsigned long)&unk_2F48 && (*(_BYTE *)(a1 - 80 + 16) & 8) != 0 )
    {
      v2 = 40000LL / (*(_DWORD *)(a1 - 40 + 8) + 2) + 4900;
    }
  }
  if ( (*(_BYTE *)(a1 + 16) & 1) != 0 )
  {
    v2 -= 1600LL;
  }
  else if ( (*(_BYTE *)(a1 + 16) & 8) != 0 )
  {
    v2 += 22500LL / (*(_DWORD *)(a1 + 8) + 2);
  }
  return v2;
}

//----- (0000000000001840) ----------------------------------------------------
long  line_cost(long a1, int a2)
{
  long v3; // rcx
  long v4; // [rsp+14h] [rbp-8h]

  if ( a1 == word_limit )
    return 0LL;
  v4 = 10 * (goal_width - a2) * (long)(10 * (goal_width - a2));
  if ( *(_QWORD *)(a1 + 32) != word_limit )
  {
    v3 = 10 * (a2 - *(_DWORD *)(a1 + 20));
    v4 += v3 * v3 / 2;
  }
  return v4;
}
// 1B60: using guessed type int goal_width;
// CB60: using guessed type long word_limit;

//----- (00000000000018F4) ----------------------------------------------------
long  put_paragraph(long a1)
{
  long result; // rax
  long i; // [rsp+18h] [rbp-8h]

  put_line((long)&unused_word_type, first_indent);
  for ( i = qword_2F40; ; i = *(_QWORD *)(i + 32) )
  {
    result = i;
    if ( i == a1 )
      break;
    put_line(i, other_indent);
  }
  return result;
}
// 2F40: using guessed type long qword_2F40;
// CB70: using guessed type int first_indent;
// CB74: using guessed type int other_indent;

//----- (0000000000001953) ----------------------------------------------------
int  put_line(long a1, int a2)
{
  long v3; // [rsp+8h] [rbp-18h]
  long v4; // [rsp+18h] [rbp-8h]

  v3 = a1;
  out_column = 0;
  put_space(prefix_indent);
  fputs_unlocked(prefix, stdout);
  out_column += prefix_length;
  put_space(a2 - out_column);
  v4 = *(_QWORD *)(a1 + 32) - 40LL;
  while ( v3 != v4 )
  {
    put_word((char **)v3);
    put_space(*(_DWORD *)(v3 + 12));
    v3 += 40LL;
  }
  put_word((char **)v3);
  last_line_length = out_column;
  return putchar_unlocked(10);
}
// 1B5C: using guessed type int prefix_length;
// 1B68: using guessed type int out_column;
// CB6C: using guessed type int prefix_indent;
// CB80: using guessed type int last_line_length;

//----- (0000000000001A1E) ----------------------------------------------------
long  put_word(char **a1)
{
  char *v1; // rax
  int v2; // edx
  long result; // rax
  int i; // [rsp+14h] [rbp-Ch]
  char *v5; // [rsp+18h] [rbp-8h]

  v5 = *a1;
  for ( i = *((_DWORD *)a1 + 2); i; --i )
  {
    v1 = v5++;
    putchar_unlocked(*v1);
  }
  v2 = *((_DWORD *)a1 + 2);
  result = (unsigned int)(v2 + out_column);
  out_column += v2;
  return result;
}
// 1B68: using guessed type int out_column;

//----- (0000000000001A80) ----------------------------------------------------
long  put_space(int a1)
{
  int v1; // eax
  long result; // rax
  int v3; // [rsp+18h] [rbp-8h]
  int v4; // [rsp+1Ch] [rbp-4h]

  v3 = out_column + a1;
  if ( tabs )
  {
    v1 = out_column + a1;
    if ( v3 < 0 )
      v1 = v3 + 7;
    v4 = 8 * (v1 >> 3);
    if ( v4 > out_column + 1 )
    {
      while ( v4 > out_column )
      {
        putchar_unlocked(9);
        out_column = 8 * (out_column / 8 + 1);
      }
    }
  }
  while ( 1 )
  {
    result = (unsigned int)out_column;
    if ( v3 <= out_column )
      break;
    putchar_unlocked(32);
    ++out_column;
  }
  return result;
}
// 1B68: using guessed type int out_column;
// CB68: using guessed type char tabs;

// nfuncs=57 queued=23 decompiled=23 lumina nreq=0 worse=0 better=0
// ALL OK, 23 function(s) have been successfully decompiled
