#define WSIZE 4 // word and header footer 사이즈를 byte로. 
#define DSIZE 8 // double word size를 byte로
#define CHUNKSIZE (1<<12) // heap을 늘릴 때 얼만큼 늘릴거냐? 4kb 분량.

#define MAX(x,y) ((x)>(y)? (x) : (y)) // x,y 중 큰 값을 가진다.

// size를 pack하고 개별 word 안의 bit를 할당 (size와 alloc을 비트연산), 헤더에서 써야하기 때문에 만듬.
#define PACK(size,alloc) ((size)| (alloc)) // alloc : 가용여부 (ex. 000) / size : block size를 의미. =>합치면 온전한 주소가 나온다.

/* address p위치에 words를 read와 write를 한다. */
#define GET(p) (*(unsigned int*)(p)) // 포인터를 써서 p를 참조한다. 주소와 값(값에는 다른 블록의 주소를 담는다.)을 알 수 있다. 다른 블록을 가리키거나 이동할 때 쓸 수 있다. 
#define PUT(p,val) (*(unsigned int*)(p)=(int)(val)) // 블록의 주소를 담는다. 위치를 담아야지 나중에 헤더나 푸터를 읽어서 이동 혹은 연결할 수 있다.

// address p위치로부터 size를 읽고 field를 할당
#define GET_SIZE(p) (GET(p) & ~0x7) // '~'은 역수니까 11111000이 됨. 비트 연산하면 000 앞에거만 가져올 수 있음. 즉, 헤더에서 블록 size만 가져오겠다.
#define GET_ALLOC(p) (GET(p) & 0x1) // 00000001이 됨. 헤더에서 가용여부만 가져오겠다.

/* given block ptr bp, header와 footer의 주소를 계산*/
#define HDRP(bp) ((char*)(bp) - WSIZE) // bp가 어디에있던 상관없이 WSIZE 앞에 위치한다.
#define FTRP(bp) ((char*)(bp) + GET_SIZE(HDRP(bp)) - DSIZE) // 헤더의 끝 지점부터 GET SIZE(블록의 사이즈)만큼 더한 다음 word를 2번빼는게(그 뒤 블록의 헤드에서 앞으로 2번) footer의 시작 위치가 된다.

/* GIVEN block ptr bp, 이전 블록과 다음 블록의 주소를 계산*/
#define NEXT_BLKP(bp) ((char*)(bp) + GET_SIZE(((char*)(bp)-WSIZE))) // 그 다음 블록의 bp 위치로 이동한다.(bp에서 해당 블록의 크기만큼 이동 -> 그 다음 블록의 헤더 뒤로 감.)
#define PREV_BLKP(bp) ((char*)(bp) - GET_SIZE(((char*)(bp) - DSIZE))) // 그 전 블록의 bp위치로 이동.(이전 블록 footer로 이동하면 그 전 블록의 사이즈를 알 수 있으니 그만큼 그 전으로 이동.)