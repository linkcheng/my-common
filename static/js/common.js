
let encrypt = function encrypt(message, aseKey) {
    //加密
    return CryptoJS.DES.encrypt(message, CryptoJS.enc.Utf8.parse(aseKey), {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7
    }).toString();
};
