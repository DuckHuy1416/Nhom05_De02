"""
F2 - Lấy thời tiết thực tế qua Open-Meteo và chuyển thành bằng chứng cho C5.

Không cần API key. Có thể truyền tọa độ hoặc tên địa điểm.
Các ngưỡng chuyển đổi dưới đây là quy ước kỹ thuật minh họa, không phải
ngưỡng dịch tễ/chẩn đoán chính thức.

Ví dụ:
    python -m src.app.thoi_tiet --place "Can Tho"
    python -m src.app.thoi_tiet --lat 10.045 --lon 105.746
"""
from __future__ import annotations

import argparse
from typing import Any

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def lay_toa_do(ten_dia_diem: str) -> dict[str, Any]:
    if not ten_dia_diem.strip():
        raise ValueError("Tên địa điểm không được để trống.")
    response = requests.get(
        GEOCODING_URL,
        params={"name": ten_dia_diem, "count": 5, "language": "vi", "format": "json"},
        timeout=15,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise LookupError(f"Không tìm thấy địa điểm {ten_dia_diem!r}.")
    selected = next(
        (item for item in results if item.get("country_code") == "VN"),
        results[0],
    )
    return {
        "ten": selected.get("name"),
        "tinh": selected.get("admin1"),
        "quoc_gia": selected.get("country"),
        "latitude": float(selected["latitude"]),
        "longitude": float(selected["longitude"]),
    }


def lay_thoi_tiet(latitude: float, longitude: float) -> dict[str, Any]:
    if not -90 <= latitude <= 90:
        raise ValueError("Vĩ độ phải nằm trong [-90, 90].")
    if not -180 <= longitude <= 180:
        raise ValueError("Kinh độ phải nằm trong [-180, 180].")

    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "weather_code",
            ],
            "timezone": "auto",
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current")
    if not current:
        raise RuntimeError("Open-Meteo không trả về trường current.")

    return {
        "latitude": payload.get("latitude", latitude),
        "longitude": payload.get("longitude", longitude),
        "timezone": payload.get("timezone"),
        "time": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "source": "Open-Meteo",
    }


def tao_bang_chung_bayes(weather: dict[str, Any]) -> list[str]:
    """
    Ánh xạ dữ liệu thời tiết sang mã sự kiện mà bayes.py đã định nghĩa.
    Chỉ tạo tối đa một trạng thái ThoiTiet để tránh bằng chứng mâu thuẫn.
    """
    humidity = weather.get("humidity_percent")
    rain = weather.get("precipitation_mm")
    wind = weather.get("wind_speed_kmh")
    code = weather.get("weather_code")
    if humidity is None or rain is None or wind is None:
        raise ValueError("Thiếu dữ liệu độ ẩm, mưa hoặc gió.")

    events: list[str] = []
    wet = float(humidity) >= 80 or float(rain) >= 1.0
    dry = float(humidity) < 60 and float(rain) == 0.0

    if wet:
        events.append("tt_am_do_cao" if float(humidity) >= 80 else "tt_mua_nhieu")
    elif dry:
        events.append("tt_kho_han")

    # WMO weather codes 45/48: sương mù; 51–67, 80–82, 95–99: mưa/dông.
    if code in (45, 48):
        if not wet:
            events.append("tt_suong_mu")
    if float(wind) >= 30 and wet:
        events.append("tt_gio_manh")

    return events


def danh_gia_nguy_co_so_bo(weather: dict[str, Any]) -> str:
    events = tao_bang_chung_bayes(weather)
    if any(event in events for event in ("tt_am_do_cao", "tt_mua_nhieu", "tt_suong_mu")):
        return (
            "Thời tiết có dấu hiệu ẩm/mưa. Nên tăng cường thăm đồng và kiểm tra "
            "triệu chứng đạo ôn; thời tiết không đủ để kết luận cây đã mắc bệnh."
        )
    if "tt_kho_han" in events:
        return (
            "Điều kiện hiện tại tương đối khô theo ngưỡng minh họa. "
            "Vẫn cần kiểm tra đồng ruộng định kỳ."
        )
    return (
        "Chưa đủ dữ liệu để xếp nhóm thời tiết. Cần tiếp tục theo dõi và kiểm tra thực tế."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Thời tiết cho Bác sĩ Lúa (Open-Meteo).")
    parser.add_argument("--place", help="Tên tỉnh/thành, ví dụ Can Tho")
    parser.add_argument("--lat", type=float, help="Vĩ độ")
    parser.add_argument("--lon", type=float, help="Kinh độ")
    args = parser.parse_args()

    if args.place:
        location = lay_toa_do(args.place)
        lat, lon = location["latitude"], location["longitude"]
        print(f"Địa điểm: {location['ten']}, {location.get('tinh')}, {location['quoc_gia']}")
    elif args.lat is not None and args.lon is not None:
        lat, lon = args.lat, args.lon
    else:
        parser.error("Cần --place hoặc đồng thời --lat và --lon.")

    weather = lay_thoi_tiet(lat, lon)
    print(f"Thời điểm: {weather['time']} ({weather['timezone']})")
    print(f"Nhiệt độ: {weather['temperature_c']} °C")
    print(f"Độ ẩm: {weather['humidity_percent']} %")
    print(f"Lượng mưa: {weather['precipitation_mm']} mm")
    print(f"Tốc độ gió: {weather['wind_speed_kmh']} km/h")
    print("Bằng chứng đưa vào mạng Bayes:", tao_bang_chung_bayes(weather) or "Không có")
    print("Đánh giá sơ bộ:", danh_gia_nguy_co_so_bo(weather))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
