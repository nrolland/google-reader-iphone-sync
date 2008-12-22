#import "SyncController.h"
#import "TCHelpers.h"
#import <stdio.h>

// and for proxy stuff:
#import <CoreFoundation/CoreFoundation.h>
#import <CFNetwork/CFProxySupport.h>


#ifdef SIMULATOR
	// the following function is not defined for the simulator. dammit.
	NSDictionary * CFNetworkCopySystemProxySettings(void){ return NULL; };
	NSArray * fakeProxySettings ( void * a, void * b) {
		dbg(@"returning a fake proxy setting");
		NSDictionary * dict = [NSDictionary dictionaryWithObject: kCFProxyTypeNone forKey: kCFProxyTypeKey];
		return [[NSArray arrayWithObject: dict] retain];
	}
	#define CFNetworkCopyProxiesForURL fakeProxySettings
	#warning "using hacky, faked proxy settings for the iphone simulator"
#else
	#define DEBUG
#endif

typedef enum { Default, FeedList, Status, Singleton } SyncType;

@implementation SyncController

NSString * escape_single_quotes(NSString * str) {
	return [str stringByReplacingOccurrencesOfString:@"'" withString:@"'\"'\"'"];
}

- (NSString *) syncCommandString:(SyncType) syncType {
	id settings = [[[UIApplication sharedApplication] delegate] settings];
	NSMutableString * extra_opts = [NSMutableString string];
	switch(syncType) {
		case FeedList:
			[extra_opts appendString: @" --tag-list-only"];
			break;
		case Status:
			[extra_opts appendString: @" --no-download"];
			break;
		case Singleton:
			[extra_opts appendString: @" --report-pid --quiet"];
			break;
		
	}
	
	if( [[self globalAppSettings] sortNewestItemsFirst] ) {
		[extra_opts appendString: @" --newest-first"];
	} else {
		dbg(@"NOT sorting newest first");
	}
	
	#ifndef SIMULATOR
		[extra_opts appendString: @" --quiet"];
	#else
		[extra_opts appendString: @" --verbose"];
	#endif
	
	NSString * shellString = [NSString stringWithFormat:@"python '%@' --show-status --aggressive --flush-output --config='%@' --output-path='%@' %@ 2>&1",
		escape_single_quotes([[settings docsPath] stringByAppendingPathComponent:@"sync/main.py"]),
		escape_single_quotes([[settings docsPath] stringByAppendingPathComponent:@"config.plist"]),
		escape_single_quotes([settings docsPath]),
		extra_opts];
	
	NSString * proxy = [self proxySettings];
	if(proxy) {
		dbg(@"using proxy string: %@", proxy);
		shellString = [NSString stringWithFormat:@"export http_proxy='%@';export https_proxy='%@';%@", escape_single_quotes(proxy), escape_single_quotes(proxy), shellString];
	}
	dbg_s(@"shell command: %@", shellString);
	return shellString;
}

- (void) syncWithType:(SyncType) syncType {
	if(syncThread && ![syncThread isFinished]) {
		dbg(@"thread is still running!");
		return;
	}

	NSString * shellString = [self syncCommandString:syncType];
	syncThread = [[BackgroundShell alloc] initWithShellCommand: shellString];
	[syncThread setDelegate: self];

	// set up the views
	[spinner setAnimating:YES];
	[spinner setHidden:NO];
	[cancelButton setHidden:YES];
	[okButton setHidden:YES];

	[syncStatusView setHidden:NO];
	[window addSubview: syncStatusView];
	[syncStatusView setAlpha: 1.0];
	[syncStatusView setFrame: [window frame]];
	[status_currentTask setText: @"Loading..."];
	[status_mainProgress setProgress: 0.0];
	[status_taskProgress setProgress: 0.0];
	[status_taskProgress setHidden:NO];
	[status_mainProgress setHidden:NO];
	
	// animate!
	[syncStatusView animateFadeIn];
	
	// reset output
	[last_output_line release];
	last_output_line = nil;
	
	// ..and go!
	[syncThread start];
}

- (IBAction) syncFeedListOnly: (id) sender {
	[self syncWithType:FeedList];
}

- (IBAction) sync: (id) sender {
	[self syncWithType: Default];
}

- (IBAction) syncStatusOnly: (id) sender {
	[self syncWithType: Status];
}

- (void) ensureSingletonWorkerAction:(id)obj {
	// setup GC pool
	NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
	
	NSString * cmd = [self syncCommandString:Singleton];
	dbg(@"Running command: %@", cmd);
	FILE * output = popen([cmd cStringUsingEncoding: NSUTF8StringEncoding], "r");
	char cline[500];
	NSString * line;
	int pid = 0;
	while(fgets(cline, sizeof(cline) / sizeof(char), output) != NULL) {
		line = [NSString stringWithCString: cline encoding: NSUTF8StringEncoding];
		dbg(@"pid got line: %@", line);
		line = [line stringByTrimmingCharactersInSet: [NSCharacterSet whitespaceCharacterSet]];
		if([line length] > 0) {
			if([line isEqualToString: @"None"]) {
				pid = 0;
				break;
			}
			pid = [line intValue];
		}
	}
	pclose(output);
	[self performSelector: @selector(dealWithRunningSync:)
		onThread:[NSThread mainThread]
		withObject:[NSNumber numberWithInt: pid]
		waitUntilDone: YES];
	[pool release];
}

- (void) dealWithRunningSync:(NSNumber *) pid_ {
	int pid = [pid_ intValue];
	dbg(@"pid = %d", pid);
	if(pid > 0) {
		sync_pid = pid;
		[[[[UIAlertView alloc]
			initWithTitle:@"GRiS Sync" message: @"There is already a sync running. It is either stuck, or a scheduled sync.\nStop it?"
			delegate:self cancelButtonTitle:@"Cancel (quit)" otherButtonTitles:@"Stop sync", nil]
				autorelease] show];
	}
}

- (void) ensureSingleton {
	dbg(@"spawning singleton check thread");
	[[[[NSThread alloc] initWithTarget:self selector: @selector(ensureSingletonWorkerAction:) object:nil] autorelease] start];
}

- (void) alertView:(id)view clickedButtonAtIndex: (int) index {
	dbg(@"alert view clicked item at index: %d", index);
	if(index == 1) { // kill it
		kill(sync_pid, SIGKILL);
	} else {
		dbg(@"exiting");
		[[UIApplication sharedApplication] terminate];
	}
}

- (IBAction) cancelSync: (id) sender {
	if(!syncThread || [syncThread isFinished]) {
		dbg(@"can't cancel sync - it's already finished!");
		return;
	}
	NSLog(@"cancelling thread...");
	last_output_line = @"Cancelled.";
	[syncThread cancel];
	[cancelButton setHidden:YES];
}

- (void) syncViewIsGone{
	[syncStatusView setHidden:YES];
	[syncStatusView removeFromSuperview];
}

- (NSString *) proxySettings {
	NSString * settings = nil;
	dbg(@"grabbing all proxy settings");
	CFDictionaryRef proxySettings = CFNetworkCopySystemProxySettings();
	NSURL * url = [NSURL URLWithString: @"http://google.com"];
	NSArray * proxyConfigs = CFNetworkCopyProxiesForURL(url, proxySettings);
	
	dbg(@"proxies: %@", proxyConfigs);
	if([proxyConfigs count] > 0) {
		NSDictionary * bestProxy = [proxyConfigs objectAtIndex: 0];
		NSString * proxyType = [bestProxy objectForKey:kCFProxyTypeKey];
		if( proxyType && proxyType != kCFProxyTypeNone) {
			dbg(@"best proxy found: %@ @ %d", bestProxy, bestProxy);
			NSString * host = [bestProxy valueForKey:kCFProxyHostNameKey];
			NSString * port = [bestProxy valueForKey:kCFProxyPortNumberKey];
			NSString * user = [bestProxy valueForKey:kCFProxyUsernameKey];
			NSString * pass = [bestProxy valueForKey:kCFProxyPasswordKey];
		
			settings = [NSString stringWithFormat:@"%@%s%@%s%@%s%@",
				user ? [user stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding] : @"",
				pass ? ":":"",
				pass ? [pass stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding] : @"",
				user ? "@":"",
				host,
				port ? ":":"",
				port ? port : @""];
		}
	}
	
	[proxyConfigs release];
	return settings;
}

- (IBAction) hideSyncView: (id)sender {
	[syncStatusView animateFadeOutThenTell:self withSelector:@selector(syncViewIsGone)];
	[db reload];
	[[[UIApplication sharedApplication] delegate] refreshItemLists];
}

// sync finished but you still want to see the report
- (void) showSyncFinished {
	[status_taskProgress setHidden:YES];
	[status_mainProgress setHidden:YES];

	[spinner setHidden:YES];
	[okButton setHidden:NO];
	[cancelButton setHidden:YES];
	[appSettings reloadFeedList];
}

#pragma mark delegate callbacks
- (void) backgroundShell:(id)shell didFinishWithSuccess:(BOOL) success {
	[status_currentTask setText:last_output_line];
	[syncThread release];
	syncThread = nil;
	[self showSyncFinished];
	if([last_output_line hasPrefix:@"Sync complete."]) {
		[self hideSyncView:self];
	}
}

- (void) backgroundShell:(id)shell didProduceOutput:(NSString *) line {
	dbg_s(@"sync output: %@", line);
	int numStatusComponents;

	if([line hasPrefix:@"STAT:"]){
		NSArray * statusComponents = [line componentsSeparatedByString:@":"];
		numStatusComponents = [statusComponents count];
		if(numStatusComponents > 1) {
			@try{
				NSString * type = [statusComponents objectAtIndex:1];
				if([type isEqualToString:@"TASK_TOTAL"]){
					// total number of tasks
					totalTasks = [[statusComponents objectAtIndex:2] integerValue];
				} else if([type isEqualToString:@"TASK_PROGRESS"]){
					// new sub-task, with optional description
					if(numStatusComponents > 3) {
						[status_currentTask setText: [statusComponents objectAtIndex:3]];
					}
					[status_mainProgress setProgress: ([[statusComponents objectAtIndex:2] floatValue] / (float)totalTasks )];
					[status_taskProgress setProgress: 0.0];
				} else if([type isEqualToString:@"SUBTASK_TOTAL"]){
					// total number of steps for current subtask
					totalStepsInCurrentTask = [[statusComponents objectAtIndex:2] integerValue];
				} else if([type isEqualToString:@"SUBTASK_PROGRESS"]){
					// progress for current subtask
					[status_taskProgress setProgress: ( [[statusComponents objectAtIndex:2] floatValue] / (float)totalStepsInCurrentTask ) ];
				} else {
					dbg(@"unknown status type: %@", type);
				}
			} @catch(NSException *e) {
				dbg(@"error occurred:\n%@", e);
			}
		}
	} else {
		[last_output_line release];
		last_output_line = [line retain];
	}
}

@end
