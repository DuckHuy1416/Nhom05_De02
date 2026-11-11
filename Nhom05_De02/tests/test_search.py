"""Đặc tả CN1; BFS chỉ là đối chứng trong test, không dùng làm lời giải đồ án."""
from collections import deque

import pytest

from src.search.astar import astar
from src.search.run import plan_route


def bfs(cells, start, goal):
    """Độ dài ngắn nhất để kiểm chứng A*, có xét vật cản."""
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (row, col), distance = queue.popleft()
        if (row, col) == goal:
            return distance
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nxt = (row + dr, col + dc)
            if (0 <= nxt[0] < len(cells) and 0 <= nxt[1] < len(cells[0])
                    and cells[nxt[0]][nxt[1]] != -1 and nxt not in seen):
                seen.add(nxt)
                queue.append((nxt, distance + 1))
    return None


@pytest.mark.parametrize("cells,start,goal", [
    ([[9, 0, 0], [0, -1, 0], [0, 0, 1]], (0, 0), (2, 2)),
    ([[9, -1, 1], [0, -1, 0], [0, 0, 0]], (0, 0), (0, 2)),
    ([[9, -1, 1]], (0, 0), (0, 2)),
    ([[9]], (0, 0), (0, 0)),
])
@pytest.mark.xfail(reason="chưa cài đặt", raises=NotImplementedError)
def test_astar_matches_bfs(cells, start, goal):
    expected = bfs(cells, start, goal)
    path = astar(cells, start, goal)
    if expected is None:
        assert path is None
        return
    assert path[0] == start and path[-1] == goal
    assert len(path) - 1 == expected
    for row, col in path:
        assert 0 <= row < len(cells) and 0 <= col < len(cells[0])
        assert cells[row][col] != -1
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
               for a, b in zip(path, path[1:]))


@pytest.mark.parametrize("algorithm", ["hill", "beam", "greedy"])
@pytest.mark.xfail(reason="chưa cài đặt", raises=NotImplementedError)
def test_route_resources_and_completion(algorithm):
    # k=1 buộc nạp; mức 3 vẫn chỉ tốn một đơn vị thuốc.
    grid = {"rows": 2, "cols": 3, "start": [0, 0], "k": 1, "p": 6,
            "cells": [[9, 3, 0], [0, -1, 1]]}
    result = plan_route(grid, 1, 6, algorithm)
    position = (0, 0)
    medicine, battery = 1, 6
    untreated = {(0, 1), (1, 2)}
    path = [position]
    returns = 0
    for event in result["su_kien"]:
        target = tuple(event["vi_tri"])
        if event["loai"] == "bay":
            assert abs(position[0] - target[0]) + abs(position[1] - target[1]) == 1
            assert 0 <= target[0] < 2 and 0 <= target[1] < 3
            assert grid["cells"][target[0]][target[1]] != -1
            battery -= 1
            position = target
            path.append(position)
            returns += position == (0, 0)
        elif event["loai"] == "phun":
            assert target == position and target in untreated
            medicine -= 1
            untreated.remove(target)
        else:
            assert event["loai"] == "nap" and target == position == (0, 0)
            medicine, battery = 1, 6
        assert 0 <= medicine <= 1 and 0 <= battery <= 6
        assert battery >= bfs(grid["cells"], position, (0, 0))
    assert not untreated and position == (0, 0)
    assert [tuple(cell) for cell in result["duong_di"]] == path
    assert result["tong_quang_duong"] == len(path) - 1
    assert result["so_lan_ve_tram"] == returns
    assert result["thoi_gian_chay"] >= 0


@pytest.mark.parametrize("k,p", [(0, 4), (1, 1)])
@pytest.mark.xfail(reason="chưa cài đặt", raises=NotImplementedError)
def test_route_rejects_invalid_or_infeasible(k, p):
    grid = {"rows": 1, "cols": 2, "start": [0, 0], "k": k, "p": p,
            "cells": [[9, 1]]}
    with pytest.raises(ValueError):
        plan_route(grid, k, p, "hill")
