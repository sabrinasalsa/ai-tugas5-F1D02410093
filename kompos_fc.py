import json
import sys

def muat_kb(nama_file):
    with open(nama_file, encoding="utf-8") as f:
        return json.load(f)

def syarat_terpenuhi(aturan, memori):
    ada = [s in memori for s in aturan["jika"]]
    return all(ada) if aturan["mode"] == "dan" else any(ada)

def fakta_dasar(kb):
    hasil_aturan = {a["maka"] for a in kb["aturan"]}
    urut = []
    for a in kb["aturan"]:
        for s in a["jika"]:
            if s not in hasil_aturan and s not in urut:
                urut.append(s)
    return urut

def tanya_user(kb):
    memori = set()
    dasar = fakta_dasar(kb)
    print(kb["judul"])
    print("Jawab y/t.")
    for i, fakta in enumerate(dasar, 1):
        teks = kb["pertanyaan"].get(fakta, f"Apakah {fakta}?")
        while True:
            jawab = input(f"{i}. {teks} (y/t) > ").strip().lower()
            if jawab in ("y", "t"):
                break
            print("   Mohon jawab y atau t.")
        if jawab == "y":
            memori.add(fakta)
    return memori


def forward_chaining(kb, memori):
    asal = {}     
    siklus = 0
    while True:
        cocok = [a for a in kb["aturan"]
                 if syarat_terpenuhi(a, memori) and a["maka"] not in memori]
        siklus += 1
        if not cocok:
            print(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break
        r = cocok[0]
        memori.add(r["maka"])
        asal[r["maka"]] = r
        print(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
    return asal


def cetak_alasan(fakta, asal, memori, tingkat=1):
    r = asal[fakta]
    terpenuhi = [s for s in r["jika"] if s in memori]
    print("  " * tingkat + f"{fakta} <- {r['id']} ({', '.join(terpenuhi)}) [sumber: {', '.join(r['sumber'])}]")
    for s in terpenuhi:
        if s in asal:                     # syarat ini sendiri hasil aturan lain
            cetak_alasan(s, asal, memori, tingkat + 1)


def main():
    nama_file = sys.argv[1] if len(sys.argv) > 1 else "kb_kompos.json"
    kb = muat_kb(nama_file)

    memori = tanya_user(kb)
    print("\nFakta awal:", ", ".join(sorted(memori)) if memori else "(tidak ada)")
    print()
    asal = forward_chaining(kb, memori)

    kesimpulan = [k for k in kb["kesimpulan_akhir"] if k in memori]
    print()
    if kesimpulan:
        print("Kesimpulan:", ", ".join(kesimpulan))
        print("Alasan:")
        for k in kesimpulan:
            cetak_alasan(k, asal, memori)
    else:
        print("Kesimpulan: tidak ada kesimpulan dari fakta yang diberikan.")
        print("Alasan: tidak ada aturan yang syaratnya terpenuhi sampai ke kesimpulan akhir.")

    print("\nCatatan:", kb["batas"])


if __name__ == "__main__":
    main()
