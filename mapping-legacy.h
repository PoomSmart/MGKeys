#include "struct.h"

// Total: 198 keys
// Deobfuscated: 183 keys (92.42%)
// Total gestalt keys: 169 keys
// Deobfuscated gestalt: 164 keys (97.04%)
// Unexplored: 5 keys

static const struct tKeyMapping keyMappingTableLegacy[] = {
    "+vrh8Iw5J9DJaSEy7n+iiw", "wlan.nan.enabled", // non-gestalt-key // iOS 14.0+ (removed in 15.0)
    "+zD41v0XRR72ItZHfisZuQ", "PTPLargeFilesCapability", // iOS 8.4+ (removed in 10.0)
    "/4LCTfMhvzuiK6b557ir5Q", "pearl-calibration-data", // non-gestalt-key // iOS 14.0+ (removed in 18.6)
    "/8aKho3RQEvq1PxPnN2ziQ", "MetalCapability", // iOS unknown
    "04zgp3uYWXAEZCOV0wrVXQ", "hardware-detents", // iOS unknown
    "061e/gd5kFdZwwe1G2qXFQ", NULL, // iOS 13.0+ (removed in 14.0)
    "0kE9ab+OYAMDszxCc5nNTw", "MusicStoreCapability", // iOS unknown
    "0tONs5niVymiPVtijnw9hg", "CallerIDCapability", // iOS unknown
    "0X+uIFfqTkodf6Lh20JY+w", "SMSCapability", // iOS unknown
    "0Ze/1/PMurdnnuNgYLsiSw", "OpenGLES1Capability", // iOS unknown
    "1BLBa4NFd3uQekgmXCBOCA", "BluetoothCapability", // iOS unknown
    "1ciXUB/TiXolnLnb9oa0+Q", "EncryptedDataPartitionCapability", // iOS unknown
    "1h6a0FG2nwMsUDVnYfaxxA", "MainScreenOrientation", // iOS unknown
    "1pkwRjExGQ/Xzy/LnAC98A", "LoadThumbnailsWhileScrollingCapability", // iOS unknown
    "1pwZX5NfL1wgOY5dftDTmA", "CameraRestriction", // iOS unknown
    "1tvy6WfYKVGumYi6Y8E5Og", "AccelerometerCapability", // iOS 17.0+ (removed in 18.6)
    "1ZJLuPSZ7T410f25nyus0g", "BluetoothLECapability", // iOS unknown
    "2RMKoChpU7jtotAG7NYV4Q", "VOIPCapability", // iOS unknown
    "3lh7gCvtytf3CQisb6LSJA", "ane", // iOS 12.0+ (removed in 14.0)
    "4/DY21tHB40GBdt7Xk8Sdg", "TouchIDCapability", // iOS unknown
    "45gPwlxIWz7Mui/RUwUikg", "DeviceNameString", // iOS unknown
    "4CQ7lOLjfmXp1J350TNTUQ", "TelephonyCapability", // iOS unknown
    "4MI3+6oztazPJ1ZI2OdWDQ", NULL, // non-gestalt-key, , iOS 8.4+ (removed in 10.0)
    "4TKtw5gG9r8CE3BlOrjLhg", "UnifiedIPodCapability", // iOS unknown
    "59MRw0x/zCNPzV6/uGS8cg", "PiezoClickerCapability", // iOS unknown
    "5JleoNS+AEM3ev96t8z0Qw", NULL, // non-gestalt-key, IOService:/, starts with A, iOS 9.0+ (removed in 9.3)
    "5Xri+ec5Inj/4XBalFenVQ", "MainScreenPitch", // iOS unknown
    "61o7Kdx4PeNILOhWfiXBtA", "h264-playback-level", // non-gestalt-key // iOS 7.0+ (removed in 8.4)
    "7NoMrNekLOY0QTFFKY3MUg", "RegionSupportsCinnamon", // iOS 12.1+ (removed in 18.6)
    "7Ukdmk/m0mDoIbgES+BgbQ", "Full6FeaturesCapability", // iOS unknown
    "84iheBmhAmsxIlcxG4a0zA", "VideoStillsCapability", // iOS 8.4+ (removed in 10.0)
    "8bazN693YkKz0MDmcZvjXw", "ExplicitContentRestriction", // iOS unknown
    "8lHIyh53plXuU5ZXCCtc1A", "AirDropRestriction", // iOS unknown
    "8P5JZjT7LnaofwK60pBM1w", "MicrophoneCapability", // iOS unknown
    "8QDlnfTo4K3713bkcH+E9A", "iPadCapability", // iOS unknown
    "8vIFqHe5lcMGo7TvbNLmyg", "home-button-type", // non-gestalt-key // iOS 10.0+ (removed in 11.0)
    "9s1QcGZXIyfHeOT8b/+m/A", "LTEDeviceCapability", // iOS unknown
    "9ZQAcDmoSgmTrmVL06N7hA", "AppleInternalInstallCapability", // iOS unknown
    "A8aFtN08Oqt21846jqnftQ", "SiriGestureCapability", // iOS 8.4+ (removed in 10.0)
    "Af/UTHptqxLPG5sy0wQTiw", "TorpedoCapability", // iOS unknown
    "AFgMLiOUXwdf4T83wrVcxw", "MMSCapability", // iOS unknown
    "AFSjHTczUWJZWdEzHqndnQ", "720pPlaybackCapability", // iOS unknown
    "aH78kNnsHDm9yHe6vSJYNw", "builtin-mics", // non-gestalt-key // iOS 7.0+ (removed in 15.0)
    "aIzBwNZS8VUrxL+9grefTA", "GameKitCapability", // iOS unknown
    "Ar0GS4uq6WcJ33OpIF14XQ", "HealthKitCapability", // iOS unknown
    "Bf5+aj/dC02mgZlX5cpEHg", "CallWaitingCapability", // iOS unknown
    "BfEIy3W3t0Wxf7Hf7LEsAw", "PearlCameraCapability", // iOS unknown
    "BfM9558OSUj9vu/OmyjLnw", "AssistantCapability", // iOS unknown
    "BhXj+5n3+0HcPoSArDGX7g", "EffectiveSecurityMode", // iOS 7.0+ (removed in 11.0)
    "bstETUHlPlCFu+l1GRvM0A", "TVOutCrossfadeCapability", // iOS unknown
    "BstyjvaCtwqls0MfbkGTSg", "DisplayMirroringCapability", // iOS 8.4+ (removed in 10.0)
    "C69C6jJjSxkwtSCq81shww", "CallForwardingCapability", // iOS unknown
    "Ca/ykCYJcbVY9gaO9SvKiQ", "YouTubeCapability", // iOS unknown
    "CgrU9s3DgLoemGDRXszlnQ", "3GVeniceCapability", // iOS unknown
    "cHla4KIe1wv0OvpRVrzy/w", "hide-non-default-apps", // iOS 7.0+ (removed in 26.0)
    "Cp9cxpL94276NKHivShdCg", "HomeScreenWallpaperCapability", // iOS unknown
    "cqjRgfBVUDsi5vrXdQOcng", "OpenGLES3Capability", // iOS unknown
    "drPpRw0Jmqcxv1XQPn/q/Q", "CameraFrontFlashCapability", // iOS 9.3+ (removed in 10.0)
    "dvaktw5A/h0zlsWpMg/COQ", "DeviceSupports64Bit", // iOS unknown
    "dZ2183tXAlFrXRtDcdiqJQ", "Peer2PeerCapability", // iOS unknown
    "E2iZGHvwvi387UKi9wC2Mg", "CameraFlashCapability", // iOS 8.4+ (removed in 10.0)
    "Ecx7M8v2wk05Fch3pFE/GA", "NikeIpodCapability", // iOS 8.4+ (removed in 10.0)
    "eDiwRLHFAmDNNPtULAcEZA", "TelephonyMaximumGeneration", // iOS unknown
    "ePAkIesI8SUJiAx8uRCcEA", "HDRImageCaptureCapability", // iOS unknown
    "EPMipOaz6R549ljzQFXEkA", "VolumeButtonCapability", // iOS 17.0+ (removed in 18.6)
    "EQvKwl1eIhCS1hb6EURKWg", NULL, // non-gestalt-key, , iOS 7.0+ (removed in 8.0)
    "F2M6lgy8EHCyR6hc00hMcg", "effective-security-mode", // non-gestalt-key // iOS 7.0+ (removed in 11.0)
    "fAwIjGT2efY3MHaGNHbCeQ", "modelIdentifier", // iOS unknown
    "FfP+vxxGg5AbBO0uzmp6rw", "GasGaugeBatteryCapability", // iOS unknown
    "FgjnMkPJPpI4C38dWETwtw", "flash", // iOS 7.0+ (removed in 14.3)
    "Fralg2R4+pkggafylKbVgw", "HearingAidLowEnergyAudioCapability", // iOS 8.4+ (removed in 10.0)
    "g/iV4vkeMLwXt8YPrhL+EQ", "front-flash", // non-gestalt-key // iOS 9.0+ (removed in 9.3)
    "G/ss4ZCOHb2osL8sLnZj7w", "reverse-zoom", // iOS unknown
    "g9b89U/AXTtd//2tEk1Dyw", "APNCapability", // iOS unknown
    "GFBh/UJXPx/WDLe2qhu/xA", "DeviceSuportsExternalDriverKit", // iOS unknown
    "GjhB2cGBYAYQHDA9fKOWNw", "PhotoAdjustmentsCapability", // iOS unknown
    "gow0CqXZBgAxbnq78oLJQQ", "PlatformStandAloneContactsCapability", // iOS unknown
    "gQxJNkIEjqfrFzqdebHB4w", "hme-in-arkit", // non-gestalt-key // iOS 13.0+ (removed in 13.4)
    "H6fcS+aUfwP3KiWwU9YybQ", "MultitaskingCapability", // iOS unknown
    "hL9+1F/mUsx9B1NfYn4T/g", "OTAActivationCapability", // iOS unknown
    "hSjeLvzobsJCklk4+pzu3g", "MarketingSOCNameString", // iOS unknown
    "htWSrEg/cfn3squdzvER/w", "MLEHW", // iOS 9.3+ (removed in 10.0)
    "hVVttq0KhS190K5SkaajpQ", "FrontFacingCameraCapability", // iOS unknown
    "Hx+k29zX4XhjYZRkYUvWpw", "studio-light-portrait-preview", // non-gestalt-key // iOS 13.0+ (removed in 14.0)
    "I+ptihXW+rMeySVUWURNiw", "mac-address-bluetooth1", // non-gestalt-key // iOS 7.1+ (removed in 15.8)
    "I2IvpG8yJdNpvO4csuB9EA", "LocationRemindersCapability", // iOS 8.4+ (removed in 10.0)
    "iAu0GZogf4TG69GSO5rHcg", "DeviceSupportsARKit", // iOS unknown
    "ibPgs24d3M4hvYwCtW6YAw", "wlan.lowlatency", // non-gestalt-key // iOS 14.0+ (removed in 15.0)
    "iSVbuFLd369ug7uTvmUtkQ", "SensitiveUICapability", // iOS unknown
    "jaHzwmQrBwNlt5n0dOa7DA", "SystemTelephonyOfAnyKindCapability", // iOS unknown
    "jewva1LRTg17HDPWdj+TLw", NULL, // iOS 9.3+ (removed in 10.0)
    "JIkPhorQU+H4FIGKvfqoUg", "TVOutSettingsCapability", // iOS unknown
    "JJfHGh5TTJt4RdbtmPioyw", "HDVideoCaptureCapability", // iOS unknown
    "jPfKgbKUk+Vl6s7DaotqIA", NULL, // iOS 9.0+ (removed in 10.0)
    "JuR8P7H4EAlo95lY7lgvtA", "WAPICapability", // iOS unknown
    "JVeuWWZ2F8AjVRs9kfKJ3Q", "WiFiCapability", // iOS unknown
    "jyEyRLza0L3StNXgFUCoTw", "GPSCapability", // iOS unknown
    "K+5Xuejc6dNaKo6szngjSg", "DisplayFCCLogosViaSoftwareCapability", // iOS unknown
    "K0deZit9WJp08kND9wq7cQ", "CellBroadcastCapability", // iOS unknown
    "k0rC7smY1sjVXxjCLHVeJA", "CellularDataCapability", // iOS unknown
    "k547UCppzO+wXiwXZRFuwg", "force-supported", // iOS 13.0+ (removed in 14.0)
    "kMHGt7N4hx12NopZFcIz6Q", "RingerSwitchCapability", // iOS 8.4+ (removed in 10.0)
    "KRT2emT8tNPMW9VUsXwT1A", NULL, // non-gestalt-key, , iOS 7.0+ (removed in 10.0)
    "kTX3vfIkwQHB9e90qFxlDg", "PhotoStreamCapability", // iOS unknown
    "KXulcwjWtgzrg+u8qILKBQ", "LocationServicesCapability", // iOS unknown
    "kZxeKVJr1te4KIfsML7vXw", NULL, // non-gestalt-key, , iOS 8.0+ (removed in 10.0)
    "L8PQcP8OFWzr3NCfs1QrrQ", NULL, // non-gestalt-key, IODeviceTree:/product/audio, starts with s, 061e/gd5kFdZwwe1G2qXFQ, iOS 13.0+ (removed in 14.0)
    "ld2eewXs5StVwdRtwYT8sw", "PersonalHotspotCapability", // iOS 8.4+ (removed in 10.0)
    "Lfx1lF4WO7V2u7mKQTQXGA", "LocalizedDeviceNameString", // iOS unknown
    "lJMvqLXN5hYqj0ulelo/1Q", "SIMCapability", // iOS unknown
    "lLP6eSW9thhnfm1jBFX21Q", "ScreenDimensionsCapability", // iOS unknown
    "lM8BH5myz/qFGeIYnsiEoQ", "HearingAidAudioEqualizationCapability", // iOS 8.4+ (removed in 10.0)
    "lp0YX+xu6UPp4SeF2oyLcQ", "EnforceCameraShutterClick", // iOS unknown
    "lrd6CRt0Uo4zpYyWWX0O0Q", "ContainsCellularRadioCapability", // iOS unknown
    "mMpmRVTiFjGCIUUH1v5aVg", "EncodeAACCapability", // iOS unknown
    "MulRZdIO3jyzkPar/CuDXA", "software-dimming-alpha", // iOS 7.0+ (removed in 10.0)
    "MWJNrFKpHkBEm8jAdJf1xw", "AirplayMirroringCapability", // iOS 8.4+ (removed in 10.0)
    "na77zbwlhy0V7shc4ORRgA", "post-effects", // non-gestalt-key // iOS 7.0+ (removed in 14.3)
    "nfoN5DvniQJQRqNth7F0fg", "HMERefreshRateInARKit", // iOS 13.0+ (removed in 13.4)
    "NnjMKIIAarYqUsQjrLAzCA", "avatar-camera", // iOS 17.0+ (removed in 18.6)
    "nPGxu4rFOh+jGGPSoUFgwA", "DictationCapability", // iOS unknown
    "nqZ6O+s733xoZqQZZ1NWRw", "AmbientLightSensorCapability", // iOS unknown
    "NwAF2cQVdjOKc7KkqR9tIA", "GyroscopeCapability", // iOS 17.0+ (removed in 18.6)
    "NXYYZO2ABdr0PLnSomHJ2w", "C2KDeviceCapability", // iOS unknown
    "o/P6XwYugOD7HAAAmhpTuw", "VoiceControlCapability", // iOS unknown
    "o2KLXtN1mTtM9u/2MpYnaA", "MagnetometerCapability", // iOS unknown
    "O3i4ewDkn5ARnjq2xIm/Sg", "MainScreenScale", // iOS unknown
    "oaIPJckrXuT73yxxtfGJAg", "EnforceGoogleMail", // iOS unknown
    "oGLRS3rALy/eJqiKMfXOxA", "DeviceSupportsHMEInARKit", // iOS 13.0+ (removed in 13.4)
    "oNUnoF4mZBXwKfYyCx0Vfw", "DelaySleepForHeadsetClickCapability", // iOS unknown
    "OwiopkU88VSKJX7zgoWPpQ", "external-driverkit", // iOS unknown
    "OySq8itgJ0AKORPMwrKkvA", "AccessibilityCapability", // iOS unknown
    "pdugFp4LGGarCxCXK0mWtg", "HardwareKeyboardCapability", // iOS unknown
    "PeKqfLHCeimBIYJfnFE9vw", "ApplicationInstallationCapability", // iOS unknown
    "pFXE4P/EKSiY0vBWvtT/HA", "HasAllFeaturesCapability", // iOS unknown
    "pKT0lcBNzQ676fjvMAbu6Q", "ProximitySensorCapability", // iOS unknown
    "po+GVxlZvPQi8BE6RHBDHQ", "DisplayPortCapability", // iOS unknown
    "pQ60lr9FHtEUdZFqLI0C+g", NULL, // non-gestalt-key, IOService:/5JleoNS+AEM3ev96t8z0Qw, starts with S, iOS 9.0+ (removed in 9.3)
    "PUbhrnwCUBxJ2bxlZeKscg", "VeniceCapability", // iOS unknown
    "PUY/n3uJEk8GSE+RjkHHAA", "video-cap", // iOS 7.0+ (removed in 14.0)
    "QAL4CoosdFzdrO2SMJflLQ", "GreenTeaDeviceCapability", // iOS unknown
    "qdJCWc+PSnu2Bpa6755rWQ", "RearFacingCameraCapability", // iOS unknown
    "QEmhOZosE0IT4YJkQWh3Dg", NULL, // iOS unknown
    "qMmeMcIsFZrRu0jfOy3I9Q", "HideNonDefaultApplicationsCapability", // iOS unknown
    "R836fJkaZ8xrq3rSCYjxSw", NULL, // non-gestalt-key, IODeviceTree:/product, starts with c, iOS 7.0+ (removed in 8.0)
    "Rh3jQ1k4bhpCfR4FimhRZw", "AppStoreCapability", // iOS unknown
    "S9ZweBMsbQwCL6t3Zpj4fg", "IOSurfaceBackedImagesCapability", // iOS unknown
    "SBe5o/DMF5Z94MS+ZzmBCA", "DeviceSupportsNFC", // iOS unknown
    "sgo5tedXL8Fn5rsAqD9yiQ", "HardwareEncodeSnapshotsCapability", // iOS unknown
    "SjED0v6tcI1c4fqvuUYAqQ", "EffectiveProductionStatus", // iOS 7.0+ (removed in 11.0)
    "SVhNgqwqzg0Lk5so04T35Q", "function-bb_ap_time_sync", // non-gestalt-key // iOS 8.0+ (removed in 9.3)
    "T9MMpvl0fu59PO8lXi/Cxg", "effective-production-status", // non-gestalt-key // iOS 7.0+ (removed in 11.0)
    "tAXYjbxUHRPtyQOYqzV8rQ", "DataPlanCapability", // iOS unknown
    "TcGqIE272OpkCMRaIOaPgw", "MarketingNameString", // iOS unknown
    "THaCQIAEgw5Zqceq9LAe0g", "HiccoughInterval", // iOS unknown
    "TphKlAdEwSp2CSJmGi/WDA", "MobileWifi", // iOS unknown
    "tpRXJz7izvvkGMRnTXaVWg", "WatchCompanionCapability", // iOS unknown
    "tRBbYA5BLkf/wzaof1WfyQ", "SIMPhonebookCapability", // iOS unknown
    "tZOIwbmkkjP5Nggu8/70dw", "MainScreenClass", // iOS unknown
    "U28TFcPMDYvyjIBpc8HZ4Q", "DeviceSupports3rdPartyHaptics", // iOS 13.0+ (removed in 14.0)
    "ubcUOmdIWpYH7dNopZCfEg", NULL, // non-gestalt-key, , iOS 9.0+ (removed in 10.0)
    "Ue0GVAyEOkP5kyQgcXKlxg", NULL, // iOS 9.3+ (removed in 10.0)
    "UKxn1HFRFlH0WCYlMr0gVg", "SimultaneousCallAndDataCurrentlySupported", // iOS unknown
    "ulPs+OBjapRJaJ6Ech3OFA", "h264-encoder", // iOS 7.0+ (removed in 11.0)
    "uOwIrmQD0GqKtBErL94XJg", "CameraCapability", // iOS unknown
    "UtO2BMC/uvWNvjPhK2EXiQ", "ARMV6ExecutionCapability", // iOS unknown
    "uX7jRkb03eqRdXSWq5ItkA", "adaptive-ui", // non-gestalt-key // iOS 7.0+ (removed in 8.4)
    "uYXqOrxG58efKTnlBA3PXw", "AdditionalTextTonesCapability", // iOS unknown
    "V3vz1JOFx829T5VapwzRxQ", "SimultaneousCallAndDataSupported", // iOS unknown
    "v5AoJC7hPGHbysTMLip12A", "SupportsTapToWake", // iOS unknown
    "V5QFNbWGgrw+UZPvgIbDvQ", "ASTC", // iOS unknown
    "VhcvUOAVhvIns8SosbTDrg", "NotGreenTeaDeviceCapability", // iOS unknown
    "Vn4SAODWQXeOOIVBe8CXTg", NULL, // non-gestalt-key, , iOS 7.0+ (removed in 10.0)
    "VOKmP/SJjhnx1AaT13J7QA", "MultitaskingGesturesCapability", // iOS unknown
    "vwZ4ohiPF3w3M1jzHbP30g", "HallEffectSensorCapability", // iOS 8.4+ (removed in 10.0)
    "WAg9taYd5sCaLcjVswnjjw", "ConferenceCallType", // iOS unknown
    "WKTZS6CQwtj1BP1m4SLo1A", "ShoeboxCapability", // iOS unknown
    "WT7hF1YDP3DfFx+hSAr25Q", "ARMV7ExecutionCapability", // iOS unknown
    "WWhvfhkzSG/RNghKi17E3A", "InternationalSettingsCapability", // iOS unknown
    "wXJsY4Sb2/qskFvLc+yfag", "ane-type", // non-gestalt-key // iOS 13.0+ (removed in 14.0)
    "x1RVzO1tUrUT+A3FOuaXew", "UMTSDeviceCapability", // iOS unknown
    "x7jCqsR180Lcm6rYguygmg", "MainScreenHeight", // iOS unknown
    "XACgWnmwo1t6swUPu+/UUQ", "AutoFocusCameraCapability", // iOS 8.4+ (removed in 10.0)
    "XcmwH6K+Nop/mDqy50Nrqw", "HorsemanCapability", // iOS unknown
    "XEp4h49dagkYL6YrtjW1Kw", "wifi-module-sn", // non-gestalt-key // iOS 8.0+ (removed in 18.6)
    "XPqbAKO9OGRsZmYTfs99Pw", "OpenGLES2Capability", // iOS unknown
    "yAP29WFvj9TYheRKoEJDIw", "MainScreenWidth", // iOS unknown
    "YH5LeF090QGZQTvT76qcBg", "HearingAidPowerReductionCapability", // iOS 8.4+ (removed in 10.0)
    "Yk5H+MlMreeaBLjv6PPFDw", "camera-front", // non-gestalt-key // iOS 7.0+ (removed in 15.8)
    "YWQYAm8X1mwtoYPwpLF6YA", "YouTubePluginCapability", // iOS unknown
    "z1AiZGX3Zz2qjXit83EHMA", "MultiTouchCapability", // iOS 17.0+ (removed in 18.6)
    "z5qxAI4VRmvofBOSFvwxPg", "HardwareSnapshotsRequirePurpleGfxCapability", // iOS unknown
    "zBxhtPJR7fFD8LYsxh2F+w", "ARMV7SExecutionCapability", // iOS unknown
    "ZGBeuNOKXTFmdM4TwXsaKQ", "VideoCameraCapability", // iOS unknown
    "ziO64HFBPR9QpsOGnkVjJQ", "HiDPICapability", // iOS unknown
    "zJUWenIp94snlzBD1cub3g", "function-button_halleffect", // non-gestalt-key // iOS 8.0+ (removed in 11.2)
    "zPSNnYDFk+x5ebOtenb3Eg", "auto-focus", // iOS 7.0+ (removed in 14.3)
    "Zv5zA+LUuFETzfX5WTbnjA", "ARM64ExecutionCapability", // iOS unknown
    NULL, NULL
};
