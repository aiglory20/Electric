/* 电控的暂定模块 */

#include <iostream>
#include <stdio.h>

using namespace std;

typedef struct {
  float x;
  float y;
} Point;

void get_points_on_edges(Point rect_points[4], Point points_on_edges[80],
                         int point_count) {
  int i, j;
  float dx, dy;
  for (i = 0; i < 4; i++) {
    // 获取当前边的起点和终点
    Point start_point = rect_points[i];
    Point end_point = rect_points[(i + 1) % 4];

    // 计算当前边的增量
    dx = (end_point.x - start_point.x) / (point_count - 1);
    dy = (end_point.y - start_point.y) / (point_count - 1);

    // 计算当前边上的20个点
    for (j = 0; j < point_count; j++) {
      Point point;
      point.x = start_point.x + j * dx;
      point.y = start_point.y + j * dy;
      points_on_edges[i * point_count + j] = point;
    }
  }
}

void error(Point center, Point points_on_edges[80] /*放全局 */) {
  int index = 0;            /*放全局 */
  int is_in = 0;            /*放全局 */
  int point_count = 20 * 4; /*放全局 */
  x_error = points_on_edges[index].x - center.x;
  y_error = points_on_edges[index].y - center.y;
  // TODO: 或许可以先移动到x，再y
  if (abs(x_error) < center.x * 0.03 and abs(y_error) < center.y * 0.03) {
    is_in += 1;
    if (is_in > 2) {
      is_in = 0;
      index += 2;
      if (index == point_count)
        index = 0;
    }
  } else {
    yaw = yaw - x_error / 30.0;     /*yaw放全局 */
    pitch = pitch - y_error / 30.0; /*pitch */
    // TODO: 电控移动的方式
    yaw_servo.angle(yaw);
    pitch_servo.angle(pitch);
  }
}

int main() {
  Point rect_points[4] = [ (194, 206), (161, 168), (212, 123), (245, 158) ];
  Point points_on_edges[80];
  int point_count = 80 / 4;
  get_points_on_edges(rect_points, points_on_edges, point_count);

  for (int i = 0; i < 80; i++) {
    float x = points_on_edges[i].x;
    float y = points_on_edges[i].y;
    // 在图像上标记点
    cout << x << "," << y << endl;
  }

  return 0;
}
