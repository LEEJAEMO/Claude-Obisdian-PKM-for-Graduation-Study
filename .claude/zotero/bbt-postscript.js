// Better BibTeX Postscript (BBT 6.7+ / BBT 7 호환)
// 설치: Zotero -> Edit -> Preferences -> Better BibTeX -> Citation keys 탭
//       -> 하단 Postscript 영역에 전체 붙여넣기 -> OK

if (item.itemType === 'journalArticle') {
  const journalMap = {
    "Nature": "Nature",
    "Nature Communications": "NatCommun",
    "Nature Nanotechnology": "NatNano",
    "Nature Physics": "NatPhys",
    "Nature Materials": "NatMater",
    "Nature Reviews Physics": "NatRevPhys",
    "Nature Electronics": "NatElectron",
    "Communications Physics": "CommunPhys",
    "Communications Materials": "CommunMater",
    "Physical Review Letters": "PRL",
    "Physical Review Research": "PRR",
    "Physical Review B": "PRB",
    "Physical Review X": "PRX",
    "Physical Review Applied": "PRApp",
    "Physical Review Materials": "PRMater",
    "Reviews of Modern Physics": "RMP",
    "Proceedings of the National Academy of Sciences": "PNAS",
    "Solid State Communications": "SSC",
    "Journal of the Physical Society of Japan": "JPSJ",
    "Science": "Science",
    "Science Advances": "SciAdv",
    "Applied Physics Letters": "APL",
    "Journal of Applied Physics": "JAP",
    "New Journal of Physics": "NJP",
    "Journal of Magnetism and Magnetic Materials": "JMMM",
    "IEEE Transactions on Magnetics": "IEEEMag",
  };

  // 이미 pinned key로 확장된 경우에는 재가공 안 함 (중복 방지)
  // base key는 formula 결과물 (예: HayashiEtAl2023)
  const currentKey = tex.citationKey;
  if (!/_.*\(.+\)$/.test(currentKey)) {
    const rawTitle = (item.title || '').toString();
    const cleanTitle = rawTitle
      .replace(/[\u2014\u2013]/g, '-')
      .replace(/[:,;\/\\?*"<>|\[\]{}]/g, '')
      .trim();
    const words = cleanTitle.split(/\s+/).slice(0, 6).join(' ');

    const journal = (item.publicationTitle || '').toString();
    let jabbr;
    if (journal in journalMap) {
      jabbr = journalMap[journal];
    } else if (journal) {
      jabbr = journal.split(/\s+/).slice(0, 2).map(w => w.slice(0, 3)).join('') || 'Other';
    } else {
      jabbr = 'Book';
    }

    tex.citationKey = `${currentKey}_${words} (${jabbr})`;
  }
}
