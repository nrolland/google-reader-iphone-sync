#import "ApplicationSettings.h"
#import "TCHelpers.h"

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
		@"/var/mobile/GRiS",
		@"/Users/tim/.GRiS",
		[@"~/GRiS" stringByExpandingTildeInPath],
		[@"~/.GRiS" stringByExpandingTildeInPath],
		nil];

	int i;
	BOOL isDir;
	for(i=0; i<[paths count]; i++) {
		testingPath = [paths objectAtIndex:i];
		if([fileManager fileExistsAtPath:testingPath isDirectory:&isDir] && isDir && [fileManager isWritableFileAtPath: testingPath]) {
			path = testingPath;
			break;
		}
	}
	
	if(path == nil) {
		// this is the last resort, when none of the above paths exist
		dbg(@"creating a new docs directory in the standard app doc directory");
		path = [[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0] stringByAppendingPathComponent: @"GRiS"];
		[TCHelpers ensureDirectoryExists: path];
	}
	NSLog(@"using docs path: %@", path);
	[self setDocsPath: path];
}

- (void) save {
	[self setLastViewedItem];
	BOOL success = [plistData writeToFile:[docsPath stringByAppendingPathComponent: plistName] atomically:YES];
	if(!success) {
		NSLog(@"FAILED saving plist");
	} else {
		dbg_s(@"saved data: %@ to file: %@", plistData, [docsPath stringByAppendingPathComponent: plistName]);
	}
}

- (void) load {
	dbg(@"loading plist");
	plistData = [[NSMutableDictionary dictionaryWithContentsOfFile:[docsPath stringByAppendingPathComponent: plistName]] retain];
	if(!plistData) {
		NSLog(@"FAILED loading plist");
		plistData = [[NSMutableDictionary dictionary] retain];
	}
	[self loadFeedList];
}

- (void) reloadFeedList {
	[self loadFeedList];
	[self setUIElements];
}

- (NSArray *) loadFeedList {
	dbg(@"loading feed list");
	NSString * contents = [NSString stringWithContentsOfFile: [docsPath stringByAppendingPathComponent: @"tag_list"] encoding:NSUTF8StringEncoding error:nil];
	id result;
	if(!contents) {
		dbg(@"no feed_list loaded");
		result = nil;
	} else {
		NSArray * originalList = [contents componentsSeparatedByString:@"\n"];
		NSMutableArray * feedList = [NSMutableArray arrayWithCapacity: [originalList count]];
		for(NSString * feed in originalList) {
			NSString * trimmedFeed = [feed stringByTrimmingCharactersInSet: [NSCharacterSet whitespaceAndNewlineCharacterSet]];
			if([feed length] > 0) {
				[feedList addObject: trimmedFeed];
			}
		}
		result = feedList;
	}
	[possibleTags release];
	possibleTags = [result retain];
	return result;
}
- (NSArray *) feedList {
	return possibleTags;
}

- (NSArray *) activeTagList {
	// the interestection of "selected" tags with the set of tags that exist according to google reader
	id tags = [self tagList];
	NSArray * result = [NSMutableArray arrayWithCapacity:[tags count]];
	for (NSString * tag in tags) {
		if([possibleTags containsObject: tag]) {
			[result addObject: tag];
		}
	}
	dbg(@"returning activeTagList: %@", result);
	return result;
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

#pragma mark UI actions

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

- (BOOL) getNavItem:(id *)navItem andDoneButton:(id*)btn forTextField:(id)sender {
	*btn = nil;
	*navItem = nil;
	if (sender == emailField || sender == passwordField) {
		dbg(@"\"done\" button for account");
		*btn = stopEditingAccountButton;
		*navItem = accountNavItem;
	} else {
		dbg(@"unknown sender:%@", sender);
	}
	
	return (*navItem && *btn);
}


- (void) setUIElements {
	[emailField setText: [self email]];
	[passwordField setText: [self password]];
	[itemsPerFeedSlider setValue:[self itemsPerFeed]];
	[itemsPerFeedLabel setText:[NSString stringWithFormat:@"%d", [self itemsPerFeed]]];
	[showReadItemsToggle setOn: [self showReadItems]];
	[feedList setSelectedFeeds: [self tagList]];
	[feedList setFeedList: possibleTags];
	for(id view in [feedsPlaceholderView subviews]) {
		[view removeFromSuperview];
	}
	id subview = possibleTags ? feedSelectionView : noFeedsView;
	[feedsPlaceholderView insertSubview: subview atIndex:0];
	CGSize frameSize = [feedsPlaceholderView bounds].size;
	CGRect frame = CGRectMake(0,0, frameSize.width, frameSize.height);
	[subview setFrame: frame];
}

#pragma mark GETTING values
- (int) itemsPerFeedValue: (id) sender {
	// - [UISlider value] just returns the UISlider object itself. How useful!
	return (int)(([[sender valueForKey:@"value"] floatValue] / 5) + 0.5) * 5;
}


- (NSString *) email     { return [plistData valueForKey:@"user"]; }
- (NSString *) password  { return [plistData valueForKey:@"password"]; }
- (id)         tagList   { 
	id tags = [plistData valueForKey:@"tagList"];
	if([[tags class] isSubclassOfClass: [@"" class]]) { // TODO: why can't I just pass the NSString class object?
		tags = [tags componentsSeparatedByString:@"\n"];
	}
	return tags;
}

- (BOOL) showReadItems   { return [[plistData valueForKey:@"showReadItems"] boolValue]; }
- (int) itemsPerFeed     {
	int val = [[plistData valueForKey:@"num_items"] intValue];
	if(val) return val;
	return 20; // default
}

- (NSString *) getLastViewedItem { return [plistData valueForKey:@"lastItemID"]; }
- (NSString *) getLastViewedTag { return [plistData valueForKey:@"lastItemTag"]; }
	
#pragma mark SETTING values
- (void) setReadItems:(BOOL) newVal {
	[plistData setValue: [NSNumber numberWithBool: newVal] forKey:@"showReadItems"];
}

- (void) setLastViewedItem {
	[plistData setValue: [[[UIApplication sharedApplication] delegate] currentItemID] forKey:@"lastItemID"];
	[plistData
		setValue: [[[[[[[UIApplication sharedApplication] delegate] mainController] navController] topViewController] delegate] tag]
		forKey:@"lastItemTag"];
}

- (void) setTagList: (NSArray *) selectedTags {
	[plistData setValue:selectedTags forKey:@"tagList"];
}

#pragma mark event handlers

- (IBAction) stringValueDidChange:(id)sender {
	NSString * key;
	if(sender == emailField) {
		key = @"user";
	} else if (sender == passwordField) {
		key = @"password";
	} else {
		NSLog(@"unknown item sent ApplicationSettings stringValueDidChange: %@", sender);
		return;
	}
	dbg(@"setting %@ = %@", key, [sender text]);
	[plistData setValue: [sender text] forKey:key];
	dbg(@"plist is now %@", plistData);
}

- (IBAction) switchValueDidChange:(id) sender {
	if(sender == showReadItemsToggle) {
		[self setReadItems: [[sender valueForKey:@"on"] boolValue]];
		[[[UIApplication sharedApplication] delegate] toggleOptions: self];
	} else {
		dbg(@"unknown sender sent switchValueDidChange to ApplicationSettings");
	}
}

// general handler for text view & text fields
- (void) textElementDidFinishEditing:(id) sender {
	dbg(@"string value changed");
	[sender resignFirstResponder];
	[self stringValueDidChange: sender];
	
	// hide any done buttons if necessary)
	id btn = nil;
	id navItem = nil;
	if([self getNavItem:&navItem andDoneButton:&btn forTextField:sender]) {
		dbg(@"removing button %@ from %@", btn, navItem);
		[navItem setRightBarButtonItem: nil];
	}
	[self stringValueDidChange:sender];
}

- (IBAction) textElementDidBeginEditing:(UITextField *)sender {
	dbg(@"text field %@ did begin editing...", sender);
	id btn = nil;
	id navItem = nil;
	if([self getNavItem:&navItem andDoneButton:&btn forTextField:sender]) {
		dbg(@"adding button %@ to %@", btn, navItem);
		[navItem setRightBarButtonItem: btn];
	}
}

// begin editing
- (IBAction) textFieldDidBeginEditing:(UITextField *)sender { [self textElementDidBeginEditing:sender]; }
- (IBAction) textViewDidBeginEditing: (UITextField *)sender { [self textElementDidBeginEditing:sender]; }

// end editing
- (IBAction) textFieldDidEndEditing:(UITextField *)sender { [self textElementDidFinishEditing:sender]; }
- (IBAction) textViewDidEndEditing: (UITextField *)sender { [self textElementDidFinishEditing:sender]; }


// handle the slider when it, er, slides...
- (IBAction) itemsPerFeedDidChange: (id) sender {
	int itemsPerFeed = [self itemsPerFeedValue: sender];
	[itemsPerFeedLabel setText: [NSString stringWithFormat: @"%d", itemsPerFeed]];
	[plistData setValue:[NSNumber numberWithInt:itemsPerFeed] forKey:@"num_items"];
	[sender setValue: itemsPerFeed];
}

@end
