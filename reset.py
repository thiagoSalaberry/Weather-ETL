import os
import shutil


def resetMetadata(file_dir: str, file_name: str) -> None:
    file_content: str = """
{
  "full": {
    "cities": []
  },
  "incremental": {
    "cities": []
  }
}
    """

    try:
        file_path = os.path.join(file_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write(file_content)
                print("✅ metadata.json fue reseteado correctamente.")
                return
        else:
            print(
                f"❌ El archivo '{file_name}' no existe en la carpeta '{file_path}'.")
    except Exception as e:
        print("❌ Error al resetear metadata.json: ", e)


def resetDatalake(dir_path: str, dir_name: str) -> None:
    dir_to_remove = os.path.join(dir_path, dir_name)

    try:
        if os.path.exists(dir_to_remove):
            shutil.rmtree(dir_to_remove)
            print(f"✅ El directorio '{dir_name}' fue eliminado correctamente.")
        else:
            print(f"❌ La carpeta '{dir_name}' no existe.")
    except Exception as e:
        print(f"❌ Error al eliminar el directorio '{dir_name}': {e}")


def resetProject():
    resetMetadata("./metadata", "metadata.json")
    resetDatalake(".", "datalake")


def main():
    resetProject()
    print("✅ Proyecto reseteado correctamente.")


main()
