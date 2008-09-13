#import "TagItem.h"
#import "tcHelpers.h"


@implementation TagItem

- (id) initWithTag: (NSString *) _tag count:(int) _count db:(id) _db {
	self = [super init];
	dbg(@"tagItem initWithTag: _tag count:_count db:_db");
	dbg(@"tagItem initWithTag: %@ count:%d db:%@", _tag, _count, _db);
	tag = [_tag retain];
	db = [_db retain];
	count = _count;
	return self;
}

- (BOOL) is_starred { return NO; }
- (BOOL) is_read    { return NO; }

- (NSString *) title {
	return tag;
}

- (void) dealloc {
	[tag release];
	[db release];
}

@end
