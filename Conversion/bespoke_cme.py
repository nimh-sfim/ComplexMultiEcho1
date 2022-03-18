"""Bespoke Python script for converting DICOM to Nifti"""

from argparse import ArgumentParser
from math import floor
import os
from shutil import move
from subprocess import run



def main():
    # Argument Parsing
    parser = ArgumentParser(
        description="Bespoke conversion script for ComplexMultiEcho1"
    )
    parser.add_argument("SOURCE", help="The root DICOM directory")
    parser.add_argument("DEST", help="The nifti destination")
    parser.add_argument("SUBJID", help="Subject identifier (01, NOT sub-01)")
    parser.add_argument(
        "--ignore", type=int, nargs="+", required=False, default=[],
        help="mr numbers to ignore as integers"
    )
    parser.add_argument(
        "--start", type=int, required=False, default=5,
        help="The mr number containing the T1w, default 5"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Run in quiet mode"
    )
    parser.add_argument(
        "--", action="store_true", dest="placeholder",
        help= (
            "Placeholder to allow you to indicate that the series of "
            "integers for --ignore has terminated. Does nothing else."
        )
    )
    args = parser.parse_args()

    if not args.quiet:
        print(f"Converting {args.SUBJID} DICOM images in {args.SOURCE}...")
        if args.start:
            print(f"Using start of {args.start}")
        if args.ignore:
            print(f"Ignoring mr numbers: {args.ignore}")

    # Harvest series numbers and create a number to description mapping
    mrn = harvest_mrn(args.SOURCE)

    if not args.quiet:
        print(f"Harvested mrn numbers from {args.DEST}: {mrn}")

    mr_used, desc = generate_series_mapping(
        args.start, args.ignore, mrn, args.SUBJID, verbose=(not args.quiet)
    )

    if not args.quiet:
        print("Made mapping:")

        for i in range(len(mr_used)):
            print(f"\t{mr_used[i]}:\t{desc[i]}")

    # Make sure dest exists
    if not os.path.exists(args.DEST):
        os.mkdir(args.DEST)

    # Run dcm2niix
    if not args.quiet:
        print("Running dcm2niix, may take a minute or two...")

    out = run_dcm2niix(args.SOURCE, args.DEST)

    # Ensure we have all of the right temp files and that they match
    # mapping
    tempfiles = [f for f in os.listdir(args.DEST) if "temp" in f and "echo" in f]
    tempn = set([fname_to_n(f) for f in tempfiles])
    for n in mr_used:
        if n not in tempn:
            raise ValueError(
                f"For some reason, series {n} has a directory but no files "
                "were generated. This is a strange circumstance that "
                "should never occur. Please check the dcm2niix output:\n"
                f"{out}"
            )
    # Iterate over our mapping to begin the great renaming process
    fmap = {}
    for n, d in zip(mr_used, desc):
        for old, new in generate_file_mapping(n, d, tempfiles).items():
            if old in fmap.keys():
                raise ValueError(
                    f"Something weird has happened; a temp file {old} "
                    "has been used twice."
                )
            fmap[old] = new

    # Print out the filename mappings
    if not args.quiet:
        print("Made new file mapping:")
        for old, new in fmap.items():
            print(f"{old} -> {new}")
        print()

    # Rename all of the things
    for old, new in fmap.items():
        for ext in (".nii", ".json"):
            os.rename(
                os.path.join(args.DEST,  old + ext),
                os.path.join(args.DEST,  new + ext)
            )

    # Re-scan the files
    contents = [s for s in os.listdir(args.DEST)]

    # Purge all remaining temporary files
    for f in os.listdir(args.DEST):
        if "temp" in f:
            os.remove(os.path.join(args.DEST, f))

    # Guarantee existence of anat dir
    anat_dir = os.path.join(args.DEST, "anat")
    if not os.path.exists(anat_dir):
        os.mkdir(anat_dir)

    # Guarantee existence of func dir
    func_dir = os.path.join(args.DEST, "func")
    if not os.path.exists(func_dir):
        os.mkdir(func_dir)

    for f in contents:
        af = os.path.join(args.DEST, f)
        if "task" in f:
            move(af, func_dir)
        elif "T1w" in f:
            move(af, anat_dir)
    
    print("Finished; check for success")


def harvest_mrn(path):
    """Harvest mr numbers from path

    Parameters
    ----------
    path: str
        The path to the DICOM data

    Returns
    -------
    list[int]: the mr numbers available
    """
    contents = os.listdir(path)
    mrdir = [d for d in contents if "mr" in d and not "-e" in d]
    mrn = [int(d.split("_")[1]) for d in mrdir]
    mrn.sort()
    return mrn


def generate_series_mapping(offset, ignore, mrn, subid, verbose=True):
    """Generate the mapping from series number to BIDS meaning

    Parameters
    ----------
    offset: int
        The mr number for the anatomical image (the project default is 5)
    ignore: list[int]
        A list of mr numbers to ignore
    mrn: list[int]
        A list of existing mr numbers
    subid: str
        The subject ID
    """
    # Offset is 1-indexed, but we're 0-indexed
    offset -= 1
    # Ignore is 1-indexed, but we're 0-indexed
    ignore = set([i-1 for i in ignore])
    # Guarantee that we're working with an in-order list of integers
    mrn.sort()
    # Initialize an empty list where each entry is an index into mrn that
    # is not going to be ignored
    midx = []
    # Iterate over existing mrns, add only indices of mrns we care about
    for i in range(len(mrn)):
        if i < offset:
            continue
        elif i >= offset and i not in ignore:
            midx.append(i)
    if verbose:
        print(f"Using runs {[mrn[i] for i in midx]}")

    # sbref, mag, phase for each epi run, plus one for anatomical expected
    # therefore check that the mrns - 1 is divisible by 3
    if not (len(midx) - 1) % 3 == 0:
        raise ValueError(
            "Expected to have 3*epi + 1 relevant mrns. Instead have "
            f"{len(midx)} ({(len(midx) - 1) % 3} leftover). "
            "Check offset and ignored settings for accuracy."
        )
    # now we start assigning meaning for each thing the BIDS way
    mdesc = [
        f"sub-{subid}_T1w",
        f"sub-{subid}_task-EpiTest_echo-%e_part-_sbref",
        f"sub-{subid}_task-EpiTest_echo-%e_part-mag_bold",
        f"sub-{subid}_task-EpiTest_echo-%e_part-phase_bold",
    ]
    # NOTE: early subjects did not have any reverse phase encode (a.k.a.
    # "blip-up, blip-down") and so did not convert the below because it was
    # not included.
    if int(subid)>=3:
        mdesc.extend(
            [f"sub-{subid}_task-EpiTestPA_echo-%e_part-_sbref",
            f"sub-{subid}_task-EpiTestPA_echo-%e_part-mag_bold",
            f"sub-{subid}_task-EpiTestPA_echo-%e_part-phase_bold"])
    # NOTE: if you want to add additional subject-specific conversion
    # requirements or scans which cannot be accessed via the --start or
    # --ignore options, add that logic above this line with an explanation
    currpos = 3
    series_sets = [
        ("wnw", 1),
        ("wnw", 2),
        ("wnw", 3),
        ("movie", 1),
        ("breathing", 1),
        ("movie", 2),
        ("breathing", 2),
    ]

    for s in series_sets:
        descs = generate_descriptions(subid, s)
        for d in descs:
            mdesc.append(d)
   
    if len(midx) > len(mdesc):
        raise ValueError(
            "Encountered more data than expected; maximum number of series "
            f"is {len(mdesc)}; encountered {len(midx)} instead."
        )

    # Remap indices to the series numbers
    rel = [mrn[i] for i in midx]

    # Truncate mdesc to be the same size as rel
    mdesc = [desc for desc, _ in zip(mdesc, rel)]

    return (rel, mdesc)


def generate_descriptions(subid, currset):
    """Generate the descriptor for a subject and set

    subject: str
        The subject ID
    currset: set(str, int)
        A pair of task and run number

    Returns
    -------
    list[str]: the 3 almost-BIDS names for this set of task and run
    """
    return [
        f"sub-{subid}_task-{currset[0]}_run-{currset[1]}_echo-%e_part-_sbref",
        f"sub-{subid}_task-{currset[0]}_run-{currset[1]}_echo-%e_part-mag_bold",
        f"sub-{subid}_task-{currset[0]}_run-{currset[1]}_echo-%e_part-phase_bold",
    ]


def run_dcm2niix(source, dest):
    command = [
        "dcm2niix",
        "-f", "temp-%s_echo-%e",
        "-z", "n",
        "-o", dest,
        source,
    ]
    result = run(command, capture_output=True)
    err = result.stderr.decode("ascii")
    out = result.stdout.decode("ascii")
    if result.returncode != 0:
        raise RuntimeError(
            "Encountered dcm2niix error. "
            f"Please review the error: {err}\n"
            f"You may also find the normal output helpful: {out}\n"
            "This really shouldn't happen.\n"
        )
    
    return out


def fname_to_n(f: str):
    """Extract the series number from a file

    Parameters
    ----------
    f: str
        The filename to extract the series number from

    Returns
    -------
    int, the series number
    """
    return int(f.split("_")[0].split("-")[1])


def fname_to_e(f: str):
    """Extrac the echo number from a file

    Parameters
    ----------
    f: str
        The filename to extract the echo number from

    Returns
    -------
    str, the echo number as a string
    """
    return f.split("_")[1].split("-")[1]


def generate_file_mapping(n, d, f):
    """Generate file mapping for a subset of temporary files

    n: int
        The series number to map
    d: str
        The string description of the file
    f: list[str]
        The list of file names that are temp files

    Returns
    -------
    dict with each relevant tempfile a key, and the new filename the value
    """
    relevant_files = [s[:-4] for s in f if fname_to_n(s) == n and "nii" in s]
    mapping = {fn: None for fn in relevant_files}
    for fn in relevant_files:
        newname = d
        # Make sure phase bit is detected if needed
        if "part-_" in newname:
            if "ph" in fn:
                newname = newname.replace("part-_", "part-phase_")
            else:
                newname = newname.replace("part-_", "part-mag_")
        elif "part-phase" in newname:
            if "ph" not in fn:
                raise ValueError(
                    f"Expected series {n} to be phase, but it is not."
                )
        elif "part-mag" in newname:
            if "ph" in fn:
                raise ValueError(
                    f"Expected series {n} to be mag, but it is not."
                )
        if "echo" in newname:
            # Replace the %e with an actual number
            newname = newname.replace("%e", fname_to_e(fn))
        mapping[fn] = newname
    return mapping


if __name__ == '__main__':
    main()
