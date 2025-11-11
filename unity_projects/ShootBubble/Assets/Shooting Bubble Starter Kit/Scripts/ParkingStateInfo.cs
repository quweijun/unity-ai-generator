using UnityEngine;
using System.Collections;

public struct ParkingStateInfo
{
    public bool final;

    public float x;
    public float y;

    public float dx;
    public float dy;

    public ParkingStateInfo(bool final, float x, float y, float dx, float dy)
    {
        this.final = final;

        this.x = x;
        this.y = y;

        this.dx = dx;
        this.dy = dy;
    }
}
