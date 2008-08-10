#import "tcItem.h"
#import "tcHelpers.h"

@implementation tcItem
@synthesize google_id, original_id, url, date, title, content, feed_name, is_read, is_starred, is_dirty;
- (id) initWithId: (NSString *) ngoogle_id
	originalId: (NSString *) noriginal_id
	date: (NSString *) ndate
	url: (NSString *) nurl
	title: (NSString *) ntitle
	content: (NSString *) ncontent
	feedName: (NSString *) nfeed_name
	is_read: (BOOL) nis_read
	is_starred:	(BOOL) nis_starred
	db: (id) ndb
{
	self = [super init];
	google_id = [ngoogle_id retain];
	original_id = [noriginal_id retain];
	date = [ndate retain];
	url = [nurl retain];
	title = [ntitle retain];
	content = [ncontent retain];
	source_db = [ndb retain];
	feed_name = [nfeed_name retain];

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

- (NSString *) domainName {
	NSString * domain = original_id;
	NSRange protocol_sep = [domain rangeOfString: @"://"];
	NSRange domainRange;
	if(protocol_sep.length > 0){
		domainRange.location = (protocol_sep.location + protocol_sep.length);
		domainRange.length = [domain length] - domainRange.location;
		domain = [domain substringWithRange: domainRange];
	}
	NSRange firstSlash = [domain rangeOfString: @"/"];
	if(firstSlash.length > 0){
		domainRange.location = 0;
		domainRange.length = firstSlash.location;
		domain = [domain substringWithRange: domainRange];
	}
	if([domain length] > 40) {
		domainRange.location = 0;
		domainRange.length = 40;
		domain = [[domain substringWithRange: domainRange] stringByAppendingString: @"..."];
	}
	return domain;
}

- (void) dealloc {
	[source_db release];
	[original_id release];
	[google_id release];
	[date release];
	[url release];
	[title release];
	[content release];
	[feed_name release];
	[super dealloc];
}

- (NSString *) dateStr {
	NSDate * now = [NSDate date];
	NSDate * then;
	NSString * dateStr;
	NSDateFormatter *timestampReader = [[[NSDateFormatter alloc] init] autorelease];
	[timestampReader setDateFormat: @"yyyyMMddHHmmss"];
	then = [timestampReader dateFromString: date];
	NSTimeInterval timePassed = [now timeIntervalSinceDate:then];
	// bah.. nstimeinterval is just a float of the number of seconds!
	int hours = timePassed / (60 * 60);
	int days = hours / 24;
	if(abs(days) < 1){
		dateStr = [NSString stringWithFormat: @"%d hours %@", hours, hours < 0 ? @"in the future":@"ago"];
	} else {
		dateStr = [NSString stringWithFormat: @"%d days %@", days, days < 0 ? @"in the future":@"ago"];
	}
	return dateStr;
}

- (NSString *) html {
	return [[NSString stringWithFormat:
		@"<html>                                                                                            \n\
			<head>                                                                                          \n\
				<meta name='viewport' content='width=500' />                                                \n\
				<link rel='stylesheet' href='template/style.css' type='text/css' />                         \n\
			</head>                                                                                         \n\
			<body>                                                                                          \n\
				<div class='post-info'>                                                                     \n\
					<h1 id='title'>                                                                         \n\
						<a href='%@'>%@</a><!-- url, title -->                                              \n\
					</h1>                                                                                   \n\
					<div class='date'>Posted %@</div>                      <!-- date -->                    \n\
					<div class='via'>                                                                       \n\
						from tag <b>%@</b> // %@<br /><br />               <!-- feed_name, domainName -->   \n\
					</div>                                                                                  \n\
				</div>                                                                                      \n\
				<div id='content'><p>                                                                       \n\
					%@                                                     <!-- content -->                 \n\
				</div>                                                                                      \n\
			</body>                                                                                         \n\
		</html>",
		url, title, [self dateStr], feed_name, [self domainName], content] autorelease];
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
