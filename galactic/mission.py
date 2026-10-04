"""Zero-dependency deterministic Galactic Mission Control (Python 3.9+)."""
import argparse
import hashlib
import heapq
import json
import math
import random


def galaxy(seed="any-pr", count=24):
    if not 2 <= count <= 200:
        raise ValueError("star count must be between 2 and 200")
    rng = random.Random(seed)
    stars, occupied = [], set()
    for index in range(count):
        while True:
            point = (rng.randrange(100), rng.randrange(100))
            if point not in occupied:
                break
        occupied.add(point)
        stars.append(dict(name=f"S{index:03d}", x=point[0], y=point[1],
                          kind=rng.choice(("ocean", "desert", "forest", "ice"))))
    return stars


def distance(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def route(stars, origin, destination, jump=30):
    """Dijkstra shortest route; None means unreachable."""
    if not math.isfinite(jump) or jump <= 0:
        raise ValueError("jump range must be finite and positive")
    lookup = {star["name"]: star for star in stars}
    if len(lookup) != len(stars):
        raise ValueError("star names must be unique")
    if origin not in lookup or destination not in lookup:
        raise ValueError("unknown origin or destination")
    best, previous, queue = {origin: 0.0}, {}, [(0.0, origin)]
    while queue:
        cost, name = heapq.heappop(queue)
        if cost > best[name]:
            continue
        if name == destination:
            path = [name]
            while path[-1] != origin:
                path.append(previous[path[-1]])
            return dict(path=path[::-1], distance=round(cost, 3), hops=len(path)-1)
        for other in stars:
            target = other["name"]
            if target == name:
                continue
            leg = distance(lookup[name], other)
            candidate = cost + leg
            if leg <= jump and candidate < best.get(target, math.inf):
                best[target], previous[target] = candidate, name
                heapq.heappush(queue, (candidate, target))
    return None


def render(stars, path=(), width=50, height=20):
    if width < 2 or height < 2:
        raise ValueError("chart dimensions must be at least 2")
    canvas = [[" " for _ in range(width)] for _ in range(height)]
    selected = set(path)
    for star in stars:
        x = min(width-1, max(0, round(star["x"] * (width-1) / 99)))
        y = min(height-1, max(0, round(star["y"] * (height-1) / 99)))
        if canvas[y][x] != "@":
            canvas[y][x] = "@" if star["name"] in selected else "*"
    border = "+" + "-" * width + "+"
    return "\n".join([border] + ["|" + "".join(row) + "|" for row in canvas]
                     + [border])


def mission(seed="any-pr", count=24, origin="S000", destination=None, jump=30):
    stars = galaxy(seed, count)
    destination = destination if destination is not None else stars[-1]["name"]
    data = dict(version=1, seed=seed, jump_range=jump, origin=origin,
                destination=destination, stars=stars,
                route=route(stars, origin, destination, jump))
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    data["fingerprint"] = hashlib.sha256(canonical.encode()).hexdigest()
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description="ANY-PR Galactic Mission Control")
    parser.add_argument("--seed", default="any-pr")
    parser.add_argument("--stars", type=int, default=24)
    parser.add_argument("--origin", default="S000")
    parser.add_argument("--destination")
    parser.add_argument("--jump", type=float, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = mission(args.seed, args.stars, args.origin, args.destination, args.jump)
    except ValueError as error:
        parser.error(str(error))
    result = data["route"]
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print("ANY-PR // GALACTIC MISSION CONTROL")
        print(render(data["stars"], result["path"] if result else ()))
        print(f"Seed: {args.seed} | Stars: {args.stars} | Jump: {args.jump}")
        print(f"Mission: {data['origin']} -> {data['destination']}")
        if result:
            print("Route: " + " -> ".join(result["path"]))
            print(f"Distance: {result['distance']} | Hops: {result['hops']}")
        else:
            print("UNREACHABLE: increase --jump or choose another destination.")
        print("Fingerprint: " + data["fingerprint"])
    return 0 if result is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
