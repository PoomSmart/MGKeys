import UIKit
import CommonCrypto

func CalculateObfuscatedKey(key: String) -> String {
    let pre = ("MGCopyAnswer" + key as String)
    var hash = [UInt8](repeating: 0, count:Int(CC_MD5_DIGEST_LENGTH))
        CC_MD5(pre, UInt32(pre.count), &hash)
    let md5Data = NSData(bytes: hash, length: Int(CC_MD5_DIGEST_LENGTH))
    let obfuscatedKey = md5Data.base64EncodedString()
    return String(obfuscatedKey.prefix(22))
}

func MD5StringForObfuscatedKey(key: String) -> String? {
    guard key.count != 0 else {
        return nil
    }
    
    let base64 = key + "=="
    let data = Data(base64Encoded: base64)
    guard data?.count == 16 else {
        return nil
    }
    
    let bytes = data!.withUnsafeBytes {
        $0.bindMemory(to: UInt8.self)
    }
    
    return bytes.map( { String(format: "%02hhx", $0) } ).joined()
}

print(CalculateObfuscatedKey(key: "DeviceIsPortableMac"))
