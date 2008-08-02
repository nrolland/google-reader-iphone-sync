#import "SyncController.h"
#import "tcHelpers.h"
#import <stdio.h>

@implementation SyncController

- (IBAction) sync: (id) sender {
	dbg(@"syncing!");
       if(syncThread) {
               if([syncThread isFinished]) {
                       [syncThread release];
                       syncThread = nil;
               } else {
                       // we're already syncing!
                       return;
               }
       }

	[spinner setAnimating:YES];
	[downloadProgrssBar setProgress:0.0];
       [cancelButton setHidden:NO];
       [okButton setHidden:YES];
	// now swap out the views
	[notSyncingView setHidden:YES];
	[syncStatusView setHidden:NO];
	[[self tabBarItem] setBadgeValue: @" "];

       syncThread = [[NSThread alloc] initWithTarget:self selector:@selector(startSync:) object:nil];
       [syncThread start];
}

- (IBAction) cancelSync: (id) sender {
       [syncThread cancel];
	[syncStatusView setHidden:YES];
	[spinner setAnimating:NO];
	[notSyncingView setHidden:NO];
	[[self tabBarItem] setBadgeValue: nil];
}

-(void) syncCompleted {
       dbg(@"sync completed successfully");
       [okButton setHidden:NO];
       [cancelButton setHidden:YES];
       [spinner setHidden:YES];
}

- (void) startSync:(id)arg {
       NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
       dbg(@"starting thread...");
       FILE *proc = [self startSyncProcess];
       while([self keepPollingForExitOfProc:proc]) {
               [pool drain];
       }
       [self syncCompleted];
       [[NSThread currentThread] exit];
}

-(FILE *) startSyncProcess {
       id settings = [[[UIApplication sharedApplication] delegate] settings];
       NSString * shellString = [NSString stringWithFormat:@"python '%@' --test --num-items='%d' --user='%@' --pass='%@' 2>&1",
               [[settings docsPath] stringByAppendingPathComponent:@"src/main.py"],
               [settings itemsPerFeed],
               [settings email],
               [settings password]];
       dbg(@"running shell command:\n%@",shellString);
       return popen([shellString cStringUsingEncoding:NSASCIIStringEncoding],"r");
}

-(BOOL) keepPollingForExitOfProc:(FILE *)proc {
       char line[200];
       dbg(@"poll...");
       char *output = fgets(line, sizeof(line), proc);
       if(output) {
               dbg(@"line:\n%s", output);
               [runningOutput setText:[NSString stringWithCString: line encoding: NSASCIIStringEncoding]];
       } else {
               dbg(@"no output...");
               return NO;
       }
       return !(feof(proc) || [syncThread isCancelled]);
}

@end
