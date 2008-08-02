#import "tcItem.h"
#import "tcHelpers.h"

@implementation tcItem
@synthesize google_id, url, date, title, content, is_read, is_starred, is_dirty;
- (id) initWithId: (NSString *) ngoogle_id
	date: (NSString *) ndate
	url: (NSString *) nurl
	title: (NSString *) ntitle
	content: (NSString *) ncontent
	is_read: (BOOL) nis_read
	is_starred:	(BOOL) nis_starred
	db: (id) ndb
{
	self = [super init];
	google_id = [ngoogle_id retain];
	date = [ndate retain];
	url = [nurl retain];
	title = [ntitle retain];
	content = [ncontent retain];
	source_db = [ndb retain];

	// booleans don't need no retaining
	is_read = nis_read;
	is_starred = nis_starred;
	is_dirty = NO;
	
	sticky_read_state = NO;
	return self;
}

- (void) save {
	[source_db updateItem:self];
}

- (void) dealloc {
	[source_db release];
	[google_id release];
	[date release];
	[url release];
	[title release];
	[content release];
	[super dealloc];
}

- (NSString *) html {
	return [[NSString stringWithFormat:
		@"<html>\n\
			<head>\n\
				<meta name='viewport' content='width=500' />\n\
				<link rel='stylesheet' href='../template/style.css' type='text/css' />\n\
			</head>\n\
			<body>\n\
				<h1 id='title'>\n\
					<a href='%@'>%@</a>\n\
				</h1>\n\
				<div class='via'>\n\
					from tag <b>%@</b><br />url %@<br /><br />\n\
				</div>\n\
				<div id='content'><p>\n\
					%@\n\
				</div>\n\
			</body>\n\
		</html>",
		url, title, @"TAG missing", url, content] autorelease];
}

- (void) userDidScrollPast {
	dbg(@"user scrolled past item %@",[self title]);
	if(sticky_read_state == NO && is_read == NO){
		is_read = YES;
		is_dirty = YES;
		[self save];
		dbg(@"is_read is now YES!");
	}
}

- (BOOL) userHasMarkedAsUnread {
	NSLog(@"user has marked as unread? %d", sticky_read_state && !is_read);
	return sticky_read_state && !is_read;
}


- (BOOL) toggleReadState {
	if (!sticky_read_state) {
		// the first "toggle" saves it - ie mark as UNread
		is_read = NO;
	} else {
		is_read = !is_read;
	}
	sticky_read_state = YES;
	is_dirty = YES;
	[self save];
	return [self userHasMarkedAsUnread];
}

- (BOOL) toggleStarredState {
	is_starred = !is_starred;
	is_dirty = YES;
	[self save];
	return is_starred;
}

@end
