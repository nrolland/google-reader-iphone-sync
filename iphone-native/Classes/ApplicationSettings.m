#import "ApplicationSettings.h"
#import "TCHelpers.h"

#define CONTENT_HEIGHT 285

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
	
	NSArray * here_path = [[NSString stringWithCString: __FILE__ encoding: NSASCIIStringEncoding] pathComponents];  // path to this file
	NSArray * base_code_path = [here_path subarrayWithRange: NSMakeRange(0, [here_path count] - 3)];                // minus file, and then up 2 directories

	NSArray * paths = [NSArray arrayWithObjects:
		[NSString stringWithFormat: @"/var/%@/GRiS", NSUserName()],     // iPhone
		[NSString stringWithFormat: @"/Users/%@/.GRiS", NSUserName()],  // simulator (in home directory)
		// (we can't use ~/.GRiS because the simulator puts ~ somewhere deep within the simulated filesystem
		[base_code_path componentsJoinedByString: @"/"],                // simulator (inside the code package - no setup required)
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
	[self saveLastViewedItem];
	BOOL success = [plistData writeToFile:[docsPath stringByAppendingPathComponent: plistName] atomically:YES];
	if(!success) {
		NSLog(@"FAILED saving plist");
	} else {
		dbg_s(@"saved data: %@ to file: %@", plistData, [docsPath stringByAppendingPathComponent: plistName]);
	}
}

- (void) load {
	plistData = [[NSMutableDictionary dictionaryWithContentsOfFile:[docsPath stringByAppendingPathComponent: plistName]] retain];
	if(!plistData) {
		NSLog(@"FAILED loading plist");
		plistData = [[NSMutableDictionary dictionary] retain];
		dbg_s(@"Loaded plist data: %@", plistData);
	}
	[self loadFeedList];
}

- (void) reloadFeedList {
	[self loadFeedList];
	[self setUIElements];
}

- (NSArray *) loadFeedList {
	NSString * contents = [NSString stringWithContentsOfFile: [docsPath stringByAppendingPathComponent: @"tag_list"] encoding:NSUTF8StringEncoding error:nil];
	id result;
	if(!contents) {
		dbg(@"no feed list loaded");
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
	return result;
}


- (id) init {
	self = [super init];
	plistName = @"config.plist";
	[self findDocsPath];
	[self load];
	return self;
}

- (void) awakeFromNib {
	[smallText setFont: [UIFont systemFontOfSize: 14.0]];
	[mainScrollView setContentSize: CGSizeMake(320, CONTENT_HEIGHT)];
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
}

- (BOOL) getNavItem:(id *)navItem andDoneButton:(id*)btn forTextField:(id)sender {
	*btn = nil;
	*navItem = nil;
	if (sender == emailField || sender == passwordField) {
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
	[navBarOnTopToggle setOn: [self navBarOnTop]];
	[openLinksInSafariToggle setOn:[self openLinksInSafari]];
	[newestItemsFirstToggle setOn: [self sortNewestItemsFirst]];
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
- (int) itemsPerFeedValue: (UISlider *) sender {
	float raw_val = [sender value];
	return (int)(roundf(raw_val / 5)) * 5; // round to the nearest multiple of 5
}

- (BOOL) boolFromKey:(NSString *) key {
	NSNumber * val = [plistData valueForKey:key];
	return val && [val boolValue];
}

- (BOOL) navBarOnTop       { return [self boolFromKey:@"navBarOnTop"]; }
- (BOOL) openLinksInSafari { return [self boolFromKey:@"openInSafari"]; }
- (BOOL) showReadItems     { return [self boolFromKey:@"showReadItems"]; }
- (BOOL) rotationLock      { return rotationLock; }
- (BOOL) sortNewestItemsFirst{ return [self boolFromKey:@"newestFirst"]; }

- (NSString *) email       { return [plistData valueForKey:@"user"]; }
- (NSString *) password    { return [plistData valueForKey:@"password"]; }

- (id) tagList     { 
	id tags = [plistData valueForKey:@"tagList"];
	if([[tags class] isSubclassOfClass: [@"" class]]) { // TODO: why can't I just pass the NSString class object?
		tags = [tags componentsSeparatedByString:@"\n"];
	}
	return tags;
}
- (int) itemsPerFeed     {
	int val = [[plistData valueForKey:@"num_items"] intValue];
	if(val) return val;
	return 20; // default
}

- (NSString *) getLastViewedItem { return [plistData valueForKey:@"lastItemID"]; }
- (NSString *) getLastViewedTag { return [plistData valueForKey:@"lastItemTag"]; }
	
#pragma mark SETTING values
- (void) saveValue:(id) val forKey:(NSString *) key {
	[plistData setValue:val forKey:key];
	[self save];
}

- (void) setBool:(BOOL) val forKey:(NSString *) key {
	[self saveValue: [NSNumber numberWithBool: val] forKey:key];
}

- (void) setNavBarOnTop:(BOOL) newVal       { [self setBool:newVal forKey:@"navBarOnTop"];  }
- (void) setOpenLinksInSafari:(BOOL) newVal { [self setBool:newVal forKey:@"openInSafari"];  }
- (void) setReadItems:(BOOL) newVal         { [self setBool:newVal forKey:@"showReadItems"]; }
- (void) setRotationLock:(BOOL) newVal      { rotationLock = newVal; } // this is intentionally not persisted
- (void) setSortNewestItemsFirst:(BOOL) newVal {
	[self setBool:newVal forKey:@"newestFirst"];
	[[self globalAppDelegate] refreshItemLists];
}

- (void) saveLastViewedItem {
	[plistData setValue:
		[[[UIApplication sharedApplication] delegate] currentItemID]
		forKey:@"lastItemID"];
	[plistData setValue:
		[[[[[[[UIApplication sharedApplication] delegate] mainController] navController] topViewController] delegate] tag]
		forKey:@"lastItemTag"];
}

- (void) setTagList: (NSArray *) selectedTags {
	[self saveValue:selectedTags forKey:@"tagList"];
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
	dbg(@"setting plist value '%@' to '%@'", key, [sender text]);
	[self saveValue: [sender text] forKey:key];
}

- (IBAction) switchValueDidChange:(id) sender {
	BOOL newValue = [[sender valueForKey:@"on"] boolValue];
	if(sender == showReadItemsToggle) {
		[self setReadItems: newValue];
	} else if(sender == rotationLockToggle) {
		[self setRotationLock: newValue];
	} else if(sender == openLinksInSafariToggle) {
		[self setOpenLinksInSafari: newValue];
	} else if(sender == newestItemsFirstToggle) {
		[self setSortNewestItemsFirst: newValue];
	} else if(sender == navBarOnTopToggle) {
		[self setNavBarOnTop: newValue];
	} else {
		dbg(@"unknown sender sent switchValueDidChange to ApplicationSettings");
	}
}

// general handler for text view & text fields
- (void) textElementDidFinishEditing:(id) sender {
	[sender resignFirstResponder];

	// hide any done buttons if necessary)
	id btn = nil;
	id navItem = nil;
	if([self getNavItem:&navItem andDoneButton:&btn forTextField:sender]) {
		[navItem setRightBarButtonItem: nil];
	}
	[self stringValueDidChange:sender];
}

- (IBAction) textElementDidBeginEditing:(UITextField *)sender {
	id btn = nil;
	id navItem = nil;
	if([self getNavItem:&navItem andDoneButton:&btn forTextField:sender]) {
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
	[self saveValue:[NSNumber numberWithInt:itemsPerFeed] forKey:@"num_items"];
	[sender setValue: itemsPerFeed];
}

@end
