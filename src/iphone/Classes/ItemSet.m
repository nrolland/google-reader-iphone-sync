#import "ItemSet.h"
#import "TCHelpers.h"

@implementation ItemSet
- (id) init {
	return [self initWithTag:nil db:nil];
}

- (id) initWithTag:(NSString *) _tag db:(id)_db {
	self = [super init];
	tag = [_tag retain];
	db = [_db retain];
	return self;
}

- (id) getItems {
	if(!itemSet) [self reload];
	return itemSet;
}

- (void) reload {
	[itemSet release];
	itemSet = [[[db itemsInTag: tag] allObjects] retain];
}

- (void) setDB:(id) _db {
	[db release];
	db = [_db retain];
	[self reload];
}

- (id) dealloc {
	[itemSet release];
	[tag release];
	[super dealloc];
}
@end
