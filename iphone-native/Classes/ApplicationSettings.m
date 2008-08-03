#import "ApplicationSettings.h"
#import "tcHelpers.h"

@implementation ApplicationSettings
- (NSString *) docsPath{ return docsPath; }
- (void) setDocsPath:newPath{
	[docsPath release];
	docsPath = [newPath retain];
}
- (void) findDocsPath {
	NSString * testingPath;
	NSFileManager * fileManager = [NSFileManager defaultManager];
	NSString * path = nil;
	NSArray * paths = [NSArray arrayWithObjects:
		@"/Users/tim/Documents/Programming/Python/reader/working",
		@"/var/mobile/GRiS",
		@"/usr/local/etc/GRis",
		@"/Users/tim/.GRiS",
		[@"~/GRiS" stringByExpandingTildeInPath],
		[@"~/.GRiS" stringByExpandingTildeInPath],
		nil];

	int i;
	BOOL isDir;
	for(i=0; i<[paths count]; i++) {
		testingPath = [paths objectAtIndex:i];
		dbg(@"trying path: %@", testingPath);
		if([fileManager fileExistsAtPath:testingPath isDirectory:&isDir] && isDir && [fileManager isWritableFileAtPath: testingPath]) {
			dbg(@"found a useful path!");
			path = testingPath;
			break;
		}
	}
	
	if(path == nil) {
		// this is the last resort, when none of the above paths exist
		dbg(@"creating a new docs directory in the standard app doc directory");
		path = [[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0] stringByAppendingPathComponent: @"GRiS"];
		[tcHelpers ensureDirectoryExists: path];
	}
	NSLog(@"using docs path: %@", path);
	[self setDocsPath: path];
}

- (void) save {
	BOOL success = [plistData writeToFile:[docsPath stringByAppendingPathComponent: plistName] atomically:YES];
	if(!success) {
		NSLog(@"FAILED saving plist");
	} else {
		dbg(@"saved data: %@ to file: %@", plistData, [docsPath stringByAppendingPathComponent: plistName]);
	}
}

- (void) load {
	dbg(@"loading plist");
	plistData = [[NSMutableDictionary dictionaryWithContentsOfFile:[docsPath stringByAppendingPathComponent: plistName]] retain];
	if(!plistData) {
		NSLog(@"FAILED loading plist");
		plistData = [[NSMutableDictionary dictionary] retain];
	}
}

- (id) init {
	self = [super init];
	plistName = @"config.plist";
	[self findDocsPath];
	[self load];
	return self;
}

-(void) awakeFromNib {
	dbg(@"AppSettings: awakeFromNib");
	[self setUIElements];
	[super awakeFromNib];
}

- (void) dealloc {
	dbg(@"settings is being dealloc'd - saving plist data.");
	[self save];
	[plistData release];
	[docsPath release];
	[plistName release];
	[super dealloc];
}

- (int) itemsPerFeedValue: (id) sender {
	// - [UISlider value] just returns the UISlider object itself. How useful!
	return (int)(([[sender valueForKey:@"value"] floatValue] / 5) + 0.5) * 5;
}

- (BOOL) textFieldShouldReturn:(UITextField *)sender{
	[sender resignFirstResponder];
	if(sender == emailField) {
		[passwordField becomeFirstResponder];
	}
	return YES;
}

- (IBAction) activatePasswordField:(id)sender {
	[passwordField becomeFirstResponder];
}
- (IBAction) deactivateBothFields:(id)sender {
	[passwordField resignFirstResponder];
	[emailField resignFirstResponder];
	[self save];
}

-(IBAction) deactivateTagListField:(id) sender {
	[tagListField resignFirstResponder];
}

- (IBAction) textFieldDidBeginEditing:(UITextField *)sender {
	if(sender == tagListField) {
		[tagListNavItem setRightBarButtonItem: stopEditingFeedsButton];
	}
}

- (IBAction) textFieldDidEndEditing:(UITextField *)sender {
	dbg(@"string value changed");
	[sender resignFirstResponder];
	[self stringValueDidChange: sender];
}

- (IBAction) itemsPerFeedDidChange: (id) sender {
	int itemsPerFeed = [self itemsPerFeedValue: sender];
	[itemsPerFeedLabel setText: [NSString stringWithFormat: @"%d", itemsPerFeed]];
	[plistData setValue:[NSNumber numberWithInt:itemsPerFeed] forKey:@"num_items"];
	[sender setValue: itemsPerFeed];
}

- (IBAction) textViewDidEndEditing: (id) sender {
	dbg(@"textviewdidendediting");
	[self stringValueDidChange:sender];
}

- (IBAction) stringValueDidChange:(id)sender {
	NSString * key;
	if(sender == emailField) {
		key = @"user";
	} else if (sender == passwordField) {
		key = @"password";
	} else if (sender == tagListField) {
		key = @"feeds";
		[tagListNavItem setRightBarButtonItem: nil];
	} else {
		NSLog(@"unknown item sent ApplicationSettings stringValueDidChange: %@", sender);
		return;
	}
	dbg(@"setting %@ = %@", key, [sender text]);
	[plistData setValue: [sender text] forKey:key];
	dbg(@"plist is now %@", plistData);
}

- (void) setUIElements {
	[emailField setText: [self email]];
	[passwordField setText: [self password]];
	[itemsPerFeedSlider setValue:[self itemsPerFeed]];
	[itemsPerFeedLabel setText:[NSString stringWithFormat:@"%d", [self itemsPerFeed]]];
}

- (NSString *) email     { return [plistData valueForKey:@"user"]; }
- (NSString *) password  { return [plistData valueForKey:@"password"]; }
- (NSString *) feeds     { return [plistData valueForKey:@"feeds"]; }
- (int) itemsPerFeed     {
	int val = [[plistData valueForKey:@"num_items"] intValue];
	if(val) return val;
	return 20; // default
}

@end
