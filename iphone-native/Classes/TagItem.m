#import "TagItem.h"
#import "tcHelpers.h"


@implementation TagItem

- (id) initWithTag: (NSString *) _tag count:(int) _count db:(id) _db {
	self = [super init];
	tag = [_tag retain];
	db = [_db retain];
	count = _count;
	return self;
}

- (BOOL) hasChildren { return YES; }
- (BOOL) is_starred { return NO; }
- (BOOL) is_read    { return NO; }
- (BOOL) count      { return count; }

- (NSString *) tagValue {
	return tag;
}

- (NSString *) descriptionText {
	return [NSString stringWithFormat: @"%d item%s", count, PLURAL(count)];
}

- (void) refreshCount {
	count = [db itemCountForTag:tag];
}

- (NSString *) title {
	return tag;
}

- (void) dealloc {
	[tag release];
	[db release];
}

@end
