async function bypassFluxus(startUrl) {
    const headers = {
      "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; GO3C Build/OPM2.171019.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.141 Mobile Safari/537.36",
      "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "accept-encoding": "gzip, deflate, br",
      "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
      "referer": "https://linkvertise.com/",
      "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
      "sec-ch-ua-mobile": "?1",
      "sec-ch-ua-platform": '"Android"',
      "sec-fetch-dest": "document",
      "sec-fetch-mode": "navigate",
      "sec-fetch-site": "cross-site",
      "sec-fetch-user": "?1",
      "upgrade-insecure-requests": "1",
    };
  
    const fluxusUrls = {
      check: "https://flux.li/android/external/check1.php?hash={hash}",
      main: "https://flux.li/android/external/main.php?hash={hash}",
    };
  
    try {
      await axios.get(startUrl, { headers });
  
      const [checkResponse, mainResponse] = await Promise.all([
        axios.get(fluxusUrls.check, { headers }),
        axios.get(fluxusUrls.main, { headers }),
      ]);
  
      const $ = cheerio.load(mainResponse.data);
      const randomStuff = $('code[style="background:#29464A;color:#F0F0F0; font-size: 13px;font-family: \'Open Sans\';"]').text().trim();
  
      return { success: true, key: randomStuff };
    } catch (error) {
      return { success: false, message: "Internal Server Error" };
    }
}
