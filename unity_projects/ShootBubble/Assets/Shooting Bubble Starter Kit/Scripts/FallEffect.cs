using UnityEngine;
using System.Collections;

public class FallEffect : MonoBehaviour
{
	public float gravity = 5.0f;
	public float initialVelocity = 10.0f;
	public float initialAngle = 0.0f;
	public float lowerLimit = 0.0f;
	
	private Transform _trans;
	private Vector2 _velocity;
	private Vector2 _gravity;
	
	private void Start()
	{
		_trans = this.transform;
		
		_velocity = new Vector2(initialVelocity * Mathf.Cos(initialAngle * Mathf.Deg2Rad),
								initialVelocity * Mathf.Sin(initialAngle * Mathf.Deg2Rad));
								
		_gravity = new Vector2(0, -gravity);
	}
	
	private void Update()
	{
		_trans.MoveBy(_velocity * Time.deltaTime + 0.5f * _gravity * Time.deltaTime * Time.deltaTime);		
		_velocity += _gravity * Time.deltaTime;
		
		if (_trans.position.y <= lowerLimit)
		{
			Destroy(this.gameObject);
		}
	}
}
