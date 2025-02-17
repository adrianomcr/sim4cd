using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class CameraControllerExternal : MonoBehaviour
{

    private TcpListener server;
    private Thread listenerThread;
    private bool isRunning = true;

    // Thread-safe queue to hold messages
    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>();

    void Start()
    {
        // Start the server on a separate thread
        listenerThread = new Thread(StartServer);
        listenerThread.Start();
    }

    void Update()
    {
        // Process messages from the queue on the main thread
        while (messageQueue.TryDequeue(out string message))
        {
            ProcessMessage(message);
        }
    }

    void StartServer()
    {
        server = new TcpListener(System.Net.IPAddress.Any, 12345);
        server.Start();

        while (isRunning)
        {
            if (server.Pending())
            {
                TcpClient client = server.AcceptTcpClient();
                NetworkStream stream = client.GetStream();

                byte[] buffer = new byte[1024];
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);

                // Enqueue the message to process it on the main thread
                messageQueue.Enqueue(message);

                client.Close();
            }
        }
    }

    void ProcessMessage(string message)
    {
        // Message format: "SET_POSITION x,y,z|SET_ROTATION x,y,z"
        string[] commands = message.Split('|');
        foreach (string command in commands)
        {
            if (command.StartsWith("SET_POSITION"))
            {
                string[] pos = command.Substring("SET_POSITION".Length).Trim().Split(',');
                if (pos.Length == 3)
                {
                    float x = float.Parse(pos[0]);
                    float y = float.Parse(pos[1]);
                    float z = float.Parse(pos[2]);
                    transform.position = new Vector3(x, y, z);
                }
            }
            else if (command.StartsWith("SET_QUAT"))
            {
                string[] rot = command.Substring("SET_QUAT".Length).Trim().Split(',');
                if (rot.Length == 4)
                {
                    float qw = float.Parse(rot[0]);
                    float qx = float.Parse(rot[1]);
                    float qy = float.Parse(rot[2]);
                    float qz = float.Parse(rot[3]);
                    transform.rotation = new Quaternion(qx, qy, qz, qw);
                }
            }
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        server.Stop();
        if (listenerThread != null)
        {
            listenerThread.Abort();
        }
    }
}

