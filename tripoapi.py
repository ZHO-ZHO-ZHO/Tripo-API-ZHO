import sys
from os import path
import os
import json
sys.path.insert(0, path.dirname(__file__))

from api.utils import tensor_to_pil_base64
from api.system import TripoAPI
from folder_paths import get_save_image_path, get_output_directory

p = os.path.dirname(os.path.realpath(__file__))


def get_tpo_api_key():
    try:
        config_path = os.path.join(p, 'config.json')
        with open(config_path, 'r') as f:  
            config = json.load(f)
        api_key = config["TRIPO_KEY"]
    except:
        print("出错啦 Error: API key is required")
        return ""
    return api_key


class TripoAPI_Zho:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["text-to-3d", "image-to-3d"],),
            },
            "optional": {
                "prompt": ("STRING", {"multiline": True}),
                "image": ("IMAGE",),  
            }
        }

    RETURN_TYPES = ("MESH_GLB", "TASK_ID")
    FUNCTION = "generate_mesh"
    CATEGORY = "TripoAPI_ZHO"

    def generate_mesh(self, mode, prompt=None, image=None):
        
        apiKey = get_tpo_api_key()
        print("apiKey:", apiKey)
        self.api = TripoAPI(apiKey)
        
        if mode == 'text-to-3d':
            if prompt is None or prompt == "":
                raise RuntimeError("Prompt is required")
            result = self.api.text_to_3d(prompt)

            if result['status'] == 'success':
                return ([result['model']], result['task_id'])
            else:
                raise RuntimeError(f"Failed to generate mesh: {result['message']}")

        elif mode == 'image-to-3d':
            if image is None:
                raise RuntimeError("Image is required")
            image_data = tensor_to_pil_base64(image)
            result = self.api.image_to_3d(image_data)

            if result['status'] == 'success':
                return ([result['model']], result['task_id'])
            else:
                raise RuntimeError(f"Failed to generate mesh: {result['message']}")

'''
class TripoAPI_Animate_ZHO:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "original_model_task_id": ("TASK_ID",),
            }
        }

    RETURN_TYPES = ("MESH_GLB", "TASK_ID")
    FUNCTION = "generate_mesh"
    CATEGORY = "TripoAPI_ZHO"

    def generate_mesh(self, original_model_task_id):
        
        apiKey = get_tpo_api_key()
        self.api = TripoAPI(apiKey)

        print("id:", original_model_task_id)
        
        if original_model_task_id is None:
             raise RuntimeError("task_id is required")
        result = self.api.f3d_to_animate(original_model_task_id)

        if result['status'] == 'success':
               return ([result['model']], result['task_id'])
        else:
            raise RuntimeError(f"Failed to generate mesh: {result['message']}")
'''


class TripoGLBViewer_ZHO:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # MESH_GLB is a custom type that represents a GLB file
                "mesh": ("MESH_GLB",)
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "display"
    CATEGORY = "TripoAPI_ZHO"

    def display(self, mesh):
        saved = []
        full_output_folder, filename, counter, subfolder, filename_prefix = get_save_image_path(
            "meshsave", get_output_directory())
        for (batch_number, single_mesh) in enumerate(mesh):
            filename_with_batch_num = filename.replace(
                "%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.glb"

            # Write the GLB content directly to a new file
            with open(path.join(full_output_folder, file), "wb") as f:
                f.write(single_mesh)
            print(f"Saved GLB file to {full_output_folder}/{file}")
            saved.append({
                "filename": file,
                "type": "output",
                "subfolder": subfolder
            })

            return {"ui": {"mesh": saved}}




NODE_CLASS_MAPPINGS = {
    "TripoAPI_Zho": TripoAPI_Zho,
    #"TripoAPI_Animate_ZHO": TripoAPI_Animate_ZHO,
    "TripoGLBViewer_ZHO": TripoGLBViewer_ZHO,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TripoAPI_Zho": "TripoAPI_Zho",
    #"TripoAPI_Animate_ZHO": "TripoAPI_Animate_ZHO",
    "TripoGLBViewer_ZHO": "TripoGLB Viewer_ZHO",
}

WEB_DIRECTORY = "./web"
