using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

internal static class Launcher
{
    [STAThread]
    private static void Main()
    {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        string python = Path.Combine(root, "runtime", "pythonw.exe");
        string builder = Path.Combine(root, "edf3_patch_builder.py");
        if (!File.Exists(python) || !File.Exists(builder))
        {
            MessageBox.Show("The application package is incomplete. Extract the entire ZIP before running it.",
                "EDF3 English Patch Builder", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return;
        }
        try
        {
            Process.Start(new ProcessStartInfo {
                FileName = python,
                Arguments = "\"" + builder + "\"",
                WorkingDirectory = root,
                UseShellExecute = false
            });
        }
        catch (Exception error)
        {
            MessageBox.Show(error.Message, "EDF3 English Patch Builder",
                MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
