#import "FeedItem.h"
#import "TCHelpers.h"

@implementation FeedItem
@synthesize google_id, original_id, url, date, title, content, feed_name, tag_name, is_read, is_starred, is_shared, is_dirty;
- (id) initWithId: (NSString *) ngoogle_id
	originalId: (NSString *) noriginal_id
	date: (NSString *) ndate
	url: (NSString *) nurl
	title: (NSString *) ntitle
	content: (NSString *) ncontent
	feedName: (NSString *) nfeed_name
	tagName: (NSString *) ntag_name
	is_read: (BOOL) nis_read
	is_starred:	(BOOL) nis_starred
	is_shared:	(BOOL) nis_shared
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
	tag_name = [ntag_name retain];

	// booleans don't need no retaining
	is_read = nis_read;
	is_starred = nis_starred;
	is_shared = nis_shared;
	is_dirty = NO;
	
	sticky_read_state = NO;
	return self;
}

- (BOOL) hasChildren { return NO; }

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
	domain = [self truncateString: domain toMaxLength: 20];
	return domain;
}

- (NSString *) truncateString: (NSString *)str toMaxLength: (int) len {
	if([str length] < len) {
		return str;
	}
	NSRange range;
	range.location = 0;
	range.length = len - 2;
	str = [[str substringWithRange: range] stringByAppendingString: @"..."];
	return str;
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
	[tag_name release];
	[super dealloc];
}

- (NSString *) descriptionText {
	return [self dateStr:NO];
}


- (NSString *) dateStr:(BOOL) longFormat {
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
	char * pastOrFuture;
	if(!longFormat) {
		pastOrFuture = "";
	} else {
		pastOrFuture = (hours < 0) ? " in the future" : " ago";
	}
	
	if(abs(days) < 1){
		dateStr = [NSString stringWithFormat: @"%d hour%s%s", hours, PLURAL(hours), pastOrFuture];
	} else {
		dateStr = [NSString stringWithFormat: @"%d day%s%s", days, PLURAL(days), pastOrFuture];
	}
	return dateStr;
}

- (NSString *) htmlForPosition:(NSString *)position_info {
	return [[NSString stringWithFormat:
		@"<html>                                                                                            \n\
			<head>                                                                                          \n\
				<meta name='viewport' content='width=500' />                                                \n\
				<link rel='stylesheet' href='template/style.css' type='text/css' />                         \n\
			</head>                                                                                         \n\
			<body>                                                                                          \n\
				<div class='post-info'>                                                                     \n\
					<h1 id='title'>                                                                         \n\
						<a href='%@'>%@</a>                                <!-- url, title -->              \n\
					</h1>                                                                                   \n\
					<div class='date'>                                                                      \n\
						%@ tag: <b>%@</b>                                   <!-- date, tag_name -->          \n\
						%@                                                 <!-- position_info -->           \n\
					</div>                                                                                  \n\
					<div class='via'>                                                                       \n\
						From <em>%@</em> (<i>%@</i>)                    <!-- feed_name, domain -->       \n\
					</div>                                                                                  \n\
				</div>                                                                                      \n\
				<div class='content'><p>                                                                    \n\
					%@                                                     <!-- content -->                 \n\
				</div>                                                                                      \n\
			</body>                                                                                         \n\
		</html>",
		url, title, [self dateStr:YES], tag_name, position_info, [self truncateString: feed_name toMaxLength: 25], [self domainName], content] autorelease];
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

- (BOOL) toggleSharedState {
	is_shared = !is_shared;
	is_dirty = YES;
	[self save];
	return is_shared;
}

@end
