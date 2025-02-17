using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class CameraControllerExternal : MonoBehaviour
{
    private TcpListener server;
    private Thread listenerThread;
    private volatile bool isRunning = true;

    // Thread-safe queue to hold messages
    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>();

    void Start()
    {
        // Start the server on a separate background thread
        listenerThread = new Thread(StartServer);
        listenerThread.IsBackground = true;
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
        try
        {
            server = new TcpListener(System.Net.IPAddress.Any, 12345);
            server.Start();

            while (isRunning)
            {
                if (server.Pending())
                {
                    try
                    {
                        TcpClient client = server.AcceptTcpClient();
                        using (NetworkStream stream = client.GetStream())
                        {
                            byte[] buffer = new byte[1024];
                            int bytesRead = stream.Read(buffer, 0, buffer.Length);
                            if (bytesRead > 0)
                            {
                                string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                                // Enqueue the message to process it on the main thread
                                messageQueue.Enqueue(message);
                            }
                        }
                        client.Close();
                    }
                    catch (SocketException ex)
                    {
                        Debug.LogError("SocketException: " + ex.Message);
                    }
                }
                else
                {
                    Thread.Sleep(25); // Prevent busy waiting
                }
            }
        }
        catch (SocketException ex)
        {
            Debug.LogError("SocketException in StartServer: " + ex.Message);
        }
        finally
        {
            if (server != null)
            {
                server.Stop();
            }
        }
    }

    void ProcessMessage(string message)
    {
        // Message format: "SET_POSITION x,y,z | SET_QUAT qw,qx,qy,qz"
        string[] commands = message.Split('|');
        foreach (string command in commands)
        {
            if (command.StartsWith("SET_POSITION"))
            {
                string[] pos = command.Substring("SET_POSITION".Length).Trim().Split(',');
                if (pos.Length == 3 &&
                    float.TryParse(pos[0], out float x) &&
                    float.TryParse(pos[1], out float y) &&
                    float.TryParse(pos[2], out float z))
                {
                    transform.position = new Vector3(x, y, z);
                }
            }
            else if (command.StartsWith("SET_QUAT"))
            {
                string[] rot = command.Substring("SET_QUAT".Length).Trim().Split(',');
                if (rot.Length == 4 &&
                    float.TryParse(rot[0], out float qw) &&
                    float.TryParse(rot[1], out float qx) &&
                    float.TryParse(rot[2], out float qy) &&
                    float.TryParse(rot[3], out float qz))
                {
                    transform.rotation = new Quaternion(qx, qy, qz, qw);
                }
            }
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        if (server != null)
        {
            server.Stop();
        }
        if (listenerThread != null && listenerThread.IsAlive)
        {
            listenerThread.Join();
        }
    }
}