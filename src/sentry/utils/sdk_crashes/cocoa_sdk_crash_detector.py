from typing import Any, Mapping, Sequence

from sentry.utils.sdk_crashes.sdk_crash_detector import SDKCrashDetector, SDKCrashDetectorConfig


class CocoaSDKCrashDetector(SDKCrashDetector):
    def __init__(self):

        config = SDKCrashDetectorConfig(
            # Explicitly use an allow list to avoid detecting SDK crashes for SDK names we don't know.
            sdk_names=[
                "sentry.cocoa",
                "sentry.cocoa.capacitor",
                "sentry.cocoa.react-native",
                "sentry.cocoa.dotnet",
                "sentry.cocoa.flutter",
                "sentry.cocoa.kmp",
                "sentry.cocoa.unity",
                "sentry.cocoa.unreal",
            ],
            # Since changing the debug image type to macho (https://github.com/getsentry/sentry-cocoa/pull/2701)
            # released in sentry-cocoa 8.2.0 (https://github.com/getsentry/sentry-cocoa/blob/main/CHANGELOG.md#820),
            # the frames contain the full paths required for detecting system frames in is_system_library_frame.
            # Therefore, we require at least sentry-cocoa 8.2.0.
            min_sdk_version="8.2.0",
            system_library_paths={"/System/Library/", "/usr/lib/"},
            sdk_frame_function_matchers={
                r"*sentrycrash*",
                r"*\[Sentry*",
                r"*(Sentry*)*",  # Objective-C class extension categories
                r"SentryMX*",  # MetricKit Swift classes
            },
            sdk_frame_filename_matchers={"Sentry**"},
        )
        super().__init__(config)

    def is_sdk_crash(self, frames: Sequence[Mapping[str, Any]]) -> bool:
        if not frames:
            return False

        # The frames are ordered from caller to callee, or oldest to youngest.
        # The last frame is the one creating the exception.
        # Therefore, we must iterate in reverse order.
        # In a first iteration of this algorithm, we checked for in_app frames, but
        # customers can change the in_app configuration, so we can't rely on that.
        # Furthermore, if they use static linking for including Sentry Cocoa, Cocoa SDK
        # frames can be marked as in_app. Therefore, the algorithm only checks if frames
        # are SDK frames or from system libraries.
        for frame in reversed(frames):
            # [SentrySDK crash] is a testing function causing a crash.
            # Therefore, we don't want to mark it a as a SDK crash.
            function = frame.get("function")
            if function and "SentrySDK crash" in function:
                return False

            if self.is_sdk_frame(frame):
                return True

            if not self.is_system_library_frame(frame):
                return False

        return False
