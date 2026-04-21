from util.hdf5_reader import HDF5Reader
import matplotlib.pyplot as plt
import argparse

def test_1(file_path: str):
    reader = HDF5Reader(file_path)
    print(reader.get_sensors())

def test_2(file_path: str):
    reader = HDF5Reader(file_path)
    print(reader.get_chunks(0, 100000000000000000))

def test_3(file_path: str):
    reader = HDF5Reader(file_path, idx_mode=True)
    current = 2000
    margin = 500
    chunk1, start, stop = reader.get_chunks(current, margin)["sensor_7E_L_85447F29887E"]
    plt.plot(chunk1[:, 0], color="red")

    reader.set_min("sensor_D5_R_A51C2DDA29D5", 300)
    chunk2, start, stop = reader.get_chunks(current, margin)["sensor_D5_R_A51C2DDA29D5"]
    plt.plot(chunk2[:, 0], color="blue")
    plt.show()

def test_4(file_path: str):
    reader = HDF5Reader(file_path, idx_mode=True)
    current = 100
    margin = 100
    chunk1, start, stop = reader.get_chunks(current, margin)["sensor_7E_L_85447F29887E"]
    plt.plot(chunk1[:, 0], color="green")
    reader.set_min("sensor_7E_L_85447F29887E", 20)
    chunk1, start, stop = reader.get_chunks(current, margin)["sensor_7E_L_85447F29887E"]
    plt.plot(chunk1[:, 0], color="red")
    plt.show()

def main():
    file_path = "C:\\Computer Science Programs\\hd_medical\\AgiMon\\align_data\\data\\hdf5_files\\session_2026-03-12_16_50_28.h5"
        
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "tests",
        nargs="*",
        help="Test names/numbers to run"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests"
    )

    args = parser.parse_args()

    test_map = {
        "1": lambda: test_1(file_path),
        "2": lambda: test_2(file_path),
        "3": lambda: test_3(file_path),
        "4": lambda: test_4(file_path),
    }

    # ---- Run all tests ----
    if args.all:
        # numeric tests first, sorted numerically
        numeric = sorted([k for k in test_map if k.isdigit()], key=int)

        # then named tests alphabetically
        named = sorted([k for k in test_map if not k.isdigit()])

        for t in numeric + named:
            print(f"\n=== Running test {t} ===")
            test_map[t]()
        return

    # ---- Run selected tests ----
    if args.tests:
        for t in args.tests:
            if t not in test_map:
                print(f"Unknown test: {t}")
                continue

            print(f"\n=== Running test {t} ===")
            test_map[t]()
        return

    parser.print_help()

if __name__ == "__main__":
    main()
